import json


def config_setter():
    with open('config.json', mode='w') as w_file:
        result = {
            k: v for k, v in
            list(zip(
                'session api_id api_hash'.split(),
                ['self', int(input("API_ID: ")), input("API_HASH: ")]
                    )
                )
            }

        json.dump(result, w_file, indent=4)
