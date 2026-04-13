import os
import subprocess
import time


def download_m3u8_to_mp4(m3u8_url: str, output_path: str) -> str | None:
    command = [
        "ffmpeg",
        "-i",
        m3u8_url,
        "-c",
        "copy",
        "-bsf:a",
        "aac_adtstoasc",
        output_path,
    ]

    try:
        subprocess.run(command, check=True)
        return output_path
    except subprocess.CalledProcessError:
        return None

def download_videos_to_local(videos: list[str]) -> list[str | None]:
    """
    下載多個影片 URL 到本地

    Args:
        videos: 影片 URL 列表

    Returns:
        本地檔案路徑列表
    """
    if not videos:
        return []

    file_paths = []
    for video in videos:
        file_path = download_m3u8_to_mp4(video, f"{time.time()}.mp4")
        file_paths.append(file_path)

    return file_paths


def download_video_to_local(video_url: str, filename: str | None = None) -> str | None:
    """
    下載單一影片 URL 到本地

    Args:
        video_url: 影片 URL
        filename: 自訂檔案名稱（可選），預設使用時間戳

    Returns:
        本地檔案路徑
    """
    if filename is None:
        filename = f"{time.time()}.mp4"

    file_path = download_m3u8_to_mp4(video_url, filename)
    print(f"下載完成: {file_path}")
    return file_path


def cleanup_local_files(file_paths: list[str]) -> None:
    """
    清理本地暫存檔案

    Args:
        file_paths: 要刪除的檔案路徑列表
    """
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


__all__ = [
    "download_m3u8_to_mp4",
    "download_video_to_local",
    "download_videos_to_local",
    "cleanup_local_files",
]
