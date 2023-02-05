
import json

# function runs inside of user_client if config file does not exist
# at the moment of when script runs. Requires user to provide his
# dev data and generates config file .json

def config_setter():
    # <desc of func>
    with open('config.json', mode='w') as w_file:
        result = {
            k: v for k, v in
            list(zip(
                'session api_id api_hash'.split(),
                f'anon {int(input("API_ID: "))} {input("API_HASH: ")}'.split()
                    )
                )
            }

        json.dump(result, w_file, indent=4)
