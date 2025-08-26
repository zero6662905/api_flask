from fastapi import FastAPI
import uvicorn
import requests
import concurrent.futures
import time
from typing import Dict, Any, Optional

app = FastAPI(docs_url="/")


def fetch_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def fetch_user_posts(user_id: int) -> Optional[list]:
    try:
        response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}/posts", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def fetch_user_albums(user_id: int) -> Optional[list]:
    try:
        response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}/albums", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def fetch_user_photos(user_id: int) -> Optional[list]:
    try:
        response = requests.get(f"https://jsonplaceholder.typicode.com/photos?userId={user_id}&_limit=10", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


@app.get("/user-dashboard/{user_id}")
async def get_user_dashboard(user_id: int):
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        profile_future = executor.submit(fetch_user_profile, user_id)
        posts_future = executor.submit(fetch_user_posts, user_id)
        albums_future = executor.submit(fetch_user_albums, user_id)
        photos_future = executor.submit(fetch_user_photos, user_id)

        profile = profile_future.result()
        posts = posts_future.result()
        albums = albums_future.result()
        photos = photos_future.result()

    stats = {
        "posts_count": len(posts) if posts else 0,
        "albums_count": len(albums) if albums else 0,
        "photos_count": len(photos) if photos else 0
    }

    response = {
        "profile": profile,
        "posts": posts,
        "albums": albums,
        "photos": photos,
        "statistics": stats,
        "execution_time_seconds": round(time.time() - start_time, 3)
    }

    return response

if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", reload=True, port=5050)
