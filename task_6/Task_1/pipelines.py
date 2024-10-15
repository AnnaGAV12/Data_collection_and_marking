# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class Task1Pipeline:
#     def process_item(self, item, spider):
#         return item

import os
from itemadapter import ItemAdapter
import csv


# class UnsplashCsvPipeline:
#     def open_spider(self, spider):
#         self.file = open('unsplash_images.csv', 'w', newline='', encoding='utf-8')
#         self.writer = csv.writer(self.file)
#         self.writer.writerow(['image_urls', 'file_paths', 'name_image', 'featured_in'])
#
#     def close_spider(self, spider):
#         self.file.close()
#
#     def process_item(self, item, spider):
#         adapter = ItemAdapter(item)
#         self.writer.writerow([
#             adapter['image_urls'][0],
#             os.path.basename(adapter['image_urls'][0].split('?')[0]),
#             adapter.get('name_image', [''])[0],
#             ', '.join(adapter.get('featured_in', []))
#         ])
#         return item

# Отдельное сохранениче через piplines
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class UnsplashImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item.get('image_urls', []):
            yield scrapy.Request(image_url)

    def file_path(self, request, response=None, info=None, *, item=None):
        category = item.get('featured_in', ['unknown_category'])[0]
        image_name = os.path.basename(request.url.split('?')[0])
        return f"{category}/{image_name}"
