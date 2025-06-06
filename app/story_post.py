import os
import logging

from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def login_user(cl:Client, username: str, password: str) -> bool:
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    login_via_session = False
    login_via_pw = False

    # Load session.json if present
    session = None
    if os.path.exists("session.json"):
        session = cl.load_settings("session.json")

    if session:
        try:
            cl.set_settings(session)
            cl.login(username, password)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(username, password)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(username, password):
                login_via_pw = True
                cl.dump_settings("session.json")
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        return False
    return True

def post_story(image_path: os.PathLike, username: str, password: str) -> Optional[str]:
    """
    Uploads a story to Instagram.
    """
    # Initiate Instagram session
    cl = Client()
    if not login_user(cl, username, password):
        return

    # Check image to upload
    if not os.path.exists(image_path):
        logger.error(f"Image not found: {image_path}")
        return

    # Upload the image
    try:
        resp = cl.photo_upload_to_story(image_path)
        media_id = resp.pk
        logger.info(f"Story {image_path} with ID: {media_id}, posted successfully.")
        return media_id
    except Exception as e:
        logger.error(f"Failed to post story: {e}")
    return

def delete_story_by_id(media_id: str) -> bool:
    """
    Deletes an Instagram story given its media ID.
    """
    # Initiate Instagram session
    cl = Client()
    if not login_user(cl):
        return False

    try:
        cl.media_delete(media_id)
        logger.info(f"Story with ID {media_id} deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to delete story with ID {media_id}: {e}")
    return False