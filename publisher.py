#!/usr/bin/env python3
import ipfshttpclient
from threading import Timer, Thread
import time
from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException
from random import randint
import typing as tp
import getpass


class Worker():
    def __init__(self):
        self.device_seed: str = None
        self.stop_thread: bool = False
        self.device_public: str = None
        self.keypair: Keypair = None

    def to_pubsub(self, data: str, endpoint: str, topic: str):
        ipfs_client = ipfshttpclient.connect(endpoint)
        ipfs_client.pubsub.publish(topic, data)
        print(f"[Pubsub] {data}")
        Timer(15, self.to_pubsub, args=(f'{{ "time": {time.time()}, "id": "mydevice", "type": "iot" }}', "/ip4/127.0.0.1/tcp/5001/http", "airalab.lighthouse.5.robonomics.eth",)).start()

    def launch_listener(self):
        if self.device_seed is None:
            try:
                with open("./config.txt") as f:
                    self.device = f.readline()
            except FileNotFoundError:
                self.get_seed()
        try:
            substrate = SubstrateInterface(
                url="wss://main.frontier.rpc.robonomics.network",
                ss58_format=32,
                type_registry_preset='substrate-node-template',
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
                        }
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
                if e.value["event_id"] == "NewLaunch" and e.params[1]["value"] == self.device_public:
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

    def to_datalog(self):
        try:
            substrate = SubstrateInterface(
                url="wss://main.frontier.rpc.robonomics.network",
                ss58_format=32,
                type_registry_preset='substrate-node-template',
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
                        }
                    }
                },
            )
        except ConnectionRefusedError:
            print("[Robonomics] Could not connect to the network. Try again")
            exit()

        while True:
            data = f'{{"time": {time.time()}, "data": {randint(0, 1000)}, "type": "iot"}}'
            call = substrate.compose_call(
                    call_module = "Datalog",
                    call_function = "record",
                    call_params = {
                        "record": data
                    }
                )
            extrinsic = substrate.create_signed_extrinsic(call=call, keypair=self.keypair)
            try:
                receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
                print(f"[Robonomics] https://robonomics.subscan.io/extrinsic/{receipt.extrinsic_hash}")
            except SubstrateRequestException as e:
                print(f'[Robonomics] Something went wrong during extrinsic submission to Robonomics: {e}')
            time.sleep(12)
            if self.stop_thread:
                break


    def get_seed(self) -> tp.Tuple[str, Keypair]:
        print("Enter seed. It won't be visible!")
        self.device_seed = getpass.getpass(prompt="Seed: ")
        try:
            self.keypair = Keypair.create_from_mnemonic(self.device_seed, ss58_format=32)
        except ValueError:
            print("Wrong seed!")
            exit()
        print("Save seed? y/n")
        response = str(input()).lower()
        if response == "y":
            with open("./config.txt", "a") as f:
                f.write(str(self.device_seed))
            print("Config file is saved!")
            
        self.device_public = self.keypair.ss58_address
        print(f"public: {self.device_public}")
        print(f"[Robonomics] Device account: {self.device_public}")


if __name__ == "__main__":
    m = Worker()
    Thread(target=m.launch_listener).start()
    Timer(15, m.to_pubsub, args=(f'{{ "time": {time.time()}, "id": "mydevice", "type": "iot" }}', "/ip4/127.0.0.1/tcp/5001/http", "airalab.lighthouse.5.robonomics.eth",)).start()




