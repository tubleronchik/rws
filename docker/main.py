#!/usr/bin/env python3
import ipfshttpclient
from threading import Timer, Thread
import time
from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException
from random import randint
import typing as tp
import os
import json


class Worker:
    def __init__(self) -> None:
        self.device_seed: str = None
        self.stop_thread: bool = False
        self.device_public: str = None
        self.keypair: Keypair = None

    def to_pubsub(self, endpoint: str, topic: str) -> None:
        ipfs_client = ipfshttpclient.connect(endpoint)
        device_id = os.environ["DEVICE_ID"]
        data = f'{{ "time": {time.time()}, "id": {device_id if device_id else "mydevice"}, "type": "iot" }}'
        ipfs_client.pubsub.publish(topic, data)
        print(f"[Pubsub] {data}")
        Timer(
            15,
            self.to_pubsub,
            args=(
                "/ip4/127.0.0.1/tcp/5001/http",
                "airalab.lighthouse.5.robonomics.eth",
            ),
        ).start()

    def launch_listener(self) -> None:
        try:
            with open("./config/config.json") as f:
                self.device_seed = json.loads((f.readline()))["seed"]
                self.keypair = Keypair.create_from_mnemonic(
                    self.device_seed, ss58_format=32
                )
                self.device_public = self.keypair.ss58_address
                print(f"[Robonomics] Device account: {self.device_public}")
        except FileNotFoundError:
            print("COnfiguration file is not found!")
            exit()
        try:
            substrate = SubstrateInterface(
                url="wss://main.frontier.rpc.robonomics.network",
                ss58_format=32,
                type_registry_preset="substrate-node-template",
                type_registry={
                    "types": {
                        "Record": "Vec<u8>",
                        "Parameter": "Bool",
                        "LaunchParameter": "Bool",
                        "<T as frame_system::Config>::AccountId": "AccountId",
                        "RingBufferItem": {
                            "type": "struct",
                            "type_mapping": [
                                ["timestamp", "Compact<u64>"],
                                ["payload", "Vec<u8>"],
                            ],
                        },
                        "RingBufferIndex": {
                            "type": "struct",
                            "type_mapping": [
                                ["start", "Compact<u64>"],
                                ["end", "Compact<u64>"],
                            ],
                        },
                    }
                },
            )
        except Exception as e:
            print(e)
            print("[Robonomics] Could not connect to the network. Try again")
            exit()
        while True:
            ch = substrate.get_chain_head()
            events = substrate.get_events(ch)
            for e in events:
                if (
                    e.value["event_id"] == "NewLaunch"
                    and e.params[1]["value"] == self.device_public
                ):
                    t = Thread(target=self.to_datalog)
                    web_address = e.params[0]["value"]
                    if e.params[2]["value"]:
                        print(f"[Robonomics] New Launch from {web_address} | ON")
                        t.start()
                        print("[Robonomics] Run device")
                    else:
                        print(f"New Launch from {web_address} | OFF")
                        self.stop_thread = True
                        print("[Robonomics] Stopping device")
            time.sleep(12)

    def to_datalog(self) -> None:
        try:
            substrate = SubstrateInterface(
                url="wss://main.frontier.rpc.robonomics.network",
                ss58_format=32,
                type_registry_preset="substrate-node-template",
                type_registry={
                    "types": {
                        "Record": "Vec<u8>",
                        "Parameter": "Bool",
                        "LaunchParameter": "Bool",
                        "<T as frame_system::Config>::AccountId": "AccountId",
                        "RingBufferItem": {
                            "type": "struct",
                            "type_mapping": [
                                ["timestamp", "Compact<u64>"],
                                ["payload", "Vec<u8>"],
                            ],
                        },
                        "RingBufferIndex": {
                            "type": "struct",
                            "type_mapping": [
                                ["start", "Compact<u64>"],
                                ["end", "Compact<u64>"],
                            ],
                        },
                    }
                },
            )
        except ConnectionRefusedError:
            print("[Robonomics] Could not connect to the network. Try again")
            exit()

        while True:
            data = (
                f'{{"time": {time.time()}, "data": {randint(0, 1000)}, "type": "iot"}}'
            )
            call = substrate.compose_call(
                call_module="Datalog",
                call_function="record",
                call_params={"record": data},
            )
            extrinsic = substrate.create_signed_extrinsic(
                call=call, keypair=self.keypair
            )
            try:
                receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
                print(
                    f"[Robonomics] https://robonomics.subscan.io/extrinsic/{receipt.extrinsic_hash}"
                )
            except SubstrateRequestException as e:
                print(
                    f"[Robonomics] Something went wrong during extrinsic submission to Robonomics: {e}"
                )
            time.sleep(12)
            if self.stop_thread:
                break


if __name__ == "__main__":
    m = Worker()
    Thread(target=m.launch_listener).start()
    Timer(
        15,
        m.to_pubsub,
        args=(
            "/ip4/127.0.0.1/tcp/5001/http",
            "airalab.lighthouse.5.robonomics.eth",
        ),
    ).start()
