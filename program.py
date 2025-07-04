from curl_cffi import requests
import uuid
import time

class avatarFx:
    def __init__(self, characterai_token):
        self.token = characterai_token
    def generate(self, image, voice_uuid, prompt):
        headers = {
            "Authorization": f"Token {self.token}",
        }
        resp = requests.get(
            "https://neo.character.ai/feature_limits/avatarfx",
            headers=headers,
            impersonate="firefox"
        )
        if (resp.status_code != 200):
            if (resp.status_code == 403):
                raise Exception("Invalid characterAi token")
            else:
                raise Exception("Requests failed")
            return
        if (resp.json()["count_remaining"] == 0):
            raise Exception("You cant generate video today anymore")
            return
        try:
            img_data = requests.get(image)
            if (img_data.status_code != 200 or img_data.content[:4] != b"\x89PNG"):
                raise Exception("Invalid image")
                return
        except:
            raise Exception("Invalid image")
            return
        
        boundary = "----WebKitFormBoundarytzEcqtDCqaTgMF3I"
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        headers["request-id"] = str(uuid.uuid4())
        data = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="blob"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + img_data.content + (
            f"\r\n--{boundary}\r\n"
            f'Content-Disposition: form-data; name="origin"\r\n\r\n'
            f"avatar_fx\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        resp = requests.post(
            "https://neo.character.ai/image/upload_private_image",
            headers=headers,
            data=data,
            impersonate="firefox"
        )
        if (resp.status_code != 200):
            raise Exception("Invalid image")
            return
        image_url = resp.json()["value"]
        
        headers["content-type"] = "application/json, text/plain, */*"
        resp = requests.post(
            "https://neo.character.ai/studio-labs/v1/generate_image_description",
            headers=headers,
            json = {"image_url":image_url, "summary_max_length":12},
            impersonate="firefox"
        )
        if (resp.status_code != 200):
            raise Exception("Image description generation failed")
            return
        img_desc = resp.json()["summary"]
        resp = requests.post(
            "https://neo.character.ai/studio-labs/v1/voice_over",
            headers=headers,
            json = {"voice_id":voice_uuid, "text":prompt},
            impersonate="firefox"
        )
        if resp.status_code != 200:
            raise Exception("Failed generating audio")
            return
        audio = resp.json()["audio_url"]
        
        resp = requests.post(
            "https://neo.character.ai/studio-labs/v1/video_generation",
            headers=headers,
            json = {"prompt":img_desc, "audio_transcript":prompt, "audio_url":audio,"image_url":image_url},
            impersonate="firefox"
        )
        if (resp.status_code != 200):
            raise Exception("Failed generating video")
            return
        videoid = resp.json()["video_id"]
        completed = False
        while completed == False:
            resp = requests.get(
                f"https://neo.character.ai/studio-labs/v1/video_generation_status/{videoid}?video_type=avatar_fx",
                headers=headers,
                impersonate="firefox"
            )
            temp = resp.json()
            if (temp["data"]["status"] == "COMPLETED"):
                completed = True
                video_url = temp["data"]["video_url"]
            else:
                print(f'{temp["data"]["message"]}')
                time.sleep(5)
        print(f"URL : {video_url}")
        return video_url