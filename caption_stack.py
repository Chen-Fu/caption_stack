from PIL import Image
from typing import List
import os
import time
from datetime import datetime


def merge_screenshots_with_subtitles(input_folder: str, output_path: str, subtitle_ratio=6):
    """
    合併指定資料夾中的所有PNG截圖，保留第一張的完整畫面，其餘只保留字幕部分
    所有圖片會調整至第一張圖片的寬度

    Args:
        input_folder: 輸入圖片所在的資料夾路徑
        output_path: 輸出圖片的路徑
        subtitle_ratio: 字幕高度比例的分母，預設為6（表示高度的1/6）
                       數字越大，字幕區域越小
    """
    # 獲取資料夾中所有的PNG檔案並按名稱排序
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
    image_files.sort()  # 按檔案名稱排序

    if len(image_files) < 2:  # 至少需要兩張圖片
        raise ValueError("資料夾中至少需要兩張PNG圖片")

    # 讀取所有圖片
    images = [Image.open(os.path.join(input_folder, path)) for path in image_files]

    # 使用第一張圖片的寬度作為標準
    target_width = images[0].size[0]

    # 調整其他圖片至第一張圖片的寬度，保持比例
    resized_images = [images[0]]  # 第一張圖片不需要調整
    for img in images[1:]:
        if img.size[0] != target_width:
            # 計算新高度，保持原始比例
            ratio = target_width / img.size[0]
            new_height = int(img.size[1] * ratio)
            # 調整圖片大小
            resized_img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
        else:
            resized_images.append(img)

    # 定義字幕區域高度
    subtitle_height = int(resized_images[0].size[1] / subtitle_ratio)

    # 計算新圖片的總高度：
    # 第一張圖完整高度 + (後續圖片數量 × 字幕高度)
    total_height = resized_images[0].size[1] + (subtitle_height * (len(resized_images) - 1))

    # 創建新的空白圖片
    new_image = Image.new('RGB', (target_width, total_height), 'white')

    # 貼上第一張完整圖片
    new_image.paste(resized_images[0], (0, 0))

    # 處理剩餘圖片的字幕部分
    for i, img in enumerate(resized_images[1:], 1):
        # 計算當前字幕應該貼上的垂直位置
        y_position = resized_images[0].size[1] + (subtitle_height * (i-1))

        # 擷取字幕部分
        subtitle = img.crop((
            0,                          # 左
            img.size[1] - subtitle_height,  # 上
            target_width,               # 右
            img.size[1]                 # 下
        ))

        # 貼上字幕
        new_image.paste(subtitle, (0, y_position))

    # 儲存結果
    new_image.save(output_path, 'PNG')
    print(f"處理的圖片檔案：{', '.join(image_files)}")
    print(f"已合併圖片並儲存至: {output_path}")
    print(f"最終圖片尺寸: {target_width}x{total_height}")
    print(f"字幕高度: {subtitle_height}像素 (1/{subtitle_ratio}的圖片高度)")

# 使用範例
if __name__ == "__main__":
    # 指定輸入資料夾和輸出檔案路徑
    # Get the current time formatted as required
    formatted_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")


    merge_screenshots_with_subtitles(
        input_folder='input_fig_folder',  # 存放PNG檔案的資料夾
        output_path='output_' + formatted_time + '.png',  # 輸出檔案路徑
        subtitle_ratio= 3.5                  # 使用 1/subtitle_ratio 高度作為字幕區域
    )
