from app.params import MODEL_TARGET, LOCAL_REGISTRY_PATH, LOCAL_DATA_PATH
from google.cloud import storage
from app.params import BUCKET_NAME
from colorama import Fore, Style
import pickle 
import time
import os
import glob

def save_model(model = None) -> None:
    """
    Persist trained model locally on the hard drive at f"{LOCAL_REGISTRY_PATH}/models/{timestamp}.h5"
    - if MODEL_TARGET='gcs', also persist it in your bucket on GCS at "models/{timestamp}.h5"
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    model_path = os.path.join(LOCAL_REGISTRY_PATH, "models", f"{timestamp}.pkl")
    with open(model_path, 'wb') as model_file: 
        pickle.dump(model, model_file)

    print("✅ Model saved locally")

    if MODEL_TARGET == "gcs":

        model_filename = model_path.split("/")[-1]
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"models/{model_filename}")
        blob.upload_from_filename(model_path)

        print("✅ Model saved to GCS")

        return None
    return None

def load_model():

    if MODEL_TARGET == "local":
        print(
            Fore.BLUE + f"\nLoad latest model from local registry..." + Style.RESET_ALL
        )

        # # Get the latest model version name by the timestamp on disk
        # local_model_directory = os.path.join(LOCAL_REGISTRY_PATH, "models")
        # local_model_paths = glob.glob(f"{local_model_directory}/*")

        # if not local_model_paths:
        #     return None

        # most_recent_model_path_on_disk = sorted(local_model_paths)[-1]

        # print(Fore.BLUE + f"\nLoad latest model from disk..." + Style.RESET_ALL)

        # latest_model = keras.models.load_model(most_recent_model_path_on_disk)

        # print("✅ Model loaded from local disk")

        return latest_model

    elif MODEL_TARGET == "gcs":
        # 🎁 We give you this piece of code as a gift. Please read it carefully! Add a breakpoint if needed!
        # print(Fore.BLUE + f"\nLoad latest model from GCS..." + Style.RESET_ALL)

        # client = storage.Client()
        # blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="model"))

        # try:
        #     latest_blob = max(blobs, key=lambda x: x.updated)
        #     latest_model_path_to_save = os.path.join(
        #         LOCAL_REGISTRY_PATH, latest_blob.name
        #     )
        #     latest_blob.download_to_filename(latest_model_path_to_save)

        #     latest_model = keras.models.load_model(latest_model_path_to_save)

        #     print("✅ Latest model downloaded from cloud storage")

        #     return latest_model
        except:
            print(f"\n❌ No model found in GCS bucket {BUCKET_NAME}")

            return None
