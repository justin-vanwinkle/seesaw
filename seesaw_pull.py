import sys
import getopt
import os
import requests
import time
from os.path import exists

headers = {}

children = [
    {
        "name":"reed",
        "child_id": "person.c3d5a121-230a-4a64-b8eb-637f4fe931b0",
        "class_id": "class.f0755104-576a-4b92-af87-639a0953a5ba"
    },
    {
        "name":"neely",
        "child_id": "person.5b4924dd-bd20-4be3-8f7a-2cd5f9b6dc5d",
        "class_id": "class.878392ae-dfb8-4e1b-8cba-cab0350cffd3"
    }
]


def download_item(filename, url, create_date, child_name, item_type):
    filepath = f"./{child_name}/{item_type}/{filename}" 
    if not exists(filepath):
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            with open(filepath, 'wb') as file:
                file.write(r.content)
                os.utime(filepath, (create_date, create_date))

def main(argv):
    bearer_token = argv[0]
    headers = {'Authorization': bearer_token}
    
    for child in children:
        # might also need to get class feed
        feed_url = f"https://app.seesaw.me/api/person/parent/class_feed?_bundle=me.see-saw.web_magiccam&_release=ss_web_prod_2022-08-26_18-59-33&_tz_offset=-14400&child_id={child['child_id']}&class_id={child['class_id']}&limit=1000"
        r = requests.get(feed_url, headers=headers)
        feed = r.json()

        items = feed['response']['items']['objects']
        for item in items:
            time.sleep(1)
            item_id = item['item']['item_id']

            item_url = f"https://app.seesaw.me/api/item_v2?item_id={item_id}"
            r = requests.get(item_url, headers=headers)
            item_page = r.json()
            
            create_date = item_page['response']['item']['create_date']

            
            if hasattr(item_page['response']['item'], 'pages'):
                print('processing page')
                pages = item_page['response']['item']['pages']['objects']
                for page in pages:
                    time.sleep(.5)
                    # TODO -- add this to the image
                    # image_caption = ""
                    # if "caption" in page:
                    #     image_caption = page['caption']

                    # if image
                    if len(page['composite_image_map']['compositeImageMap']) == 0:
                        try:
                            filename = f"{page['item_page_id']}.jpg"
                            item_url = page['composite_image_url']
                            download_item(filename, item_url, create_date, child["name"], item_type="image",)
                        except:
                            print("failed on image")
                            print(page)

                    else:
                        if (page['composite_image_map']['compositeImageMap'][0]['actions'][0]['action'] == "link"):
                            print(f"Title: {page['composite_image_map']['compositeImageMap'][0]['actions'][0]['payload']['externalLinkDetails']['title']}")
                            print(f"Link: {page['composite_image_map']['compositeImageMap'][0]['actions'][0]['payload']['destination']}")
                            print(f"Caption: {page['caption']}")
                            print("----------")

                        else:
                            # this is a video
                            filename = f"{page['item_page_id']}.mov"
                            item_url = page['composite_image_map']['compositeImageMap'][0]['actions'][0]['payload']['videoSrc']
                            download_item(filename, item_url, create_date, child["name"], item_type="video")
               
            else:
                # print(item_page['response']['item'].__dir__())
                print(item_page['response']['item']['items'])
                
if __name__ == "__main__":
    main(sys.argv[1:])
