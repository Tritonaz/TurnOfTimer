from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation


def get_active_audio_sessions(threshold=0.005):
    sessions = AudioUtilities.GetAllSessions()
    active_sessions = []

    for session in sessions:
        if session.Process is None:
            continue
        try:
            meter = session._ctl.QueryInterface(IAudioMeterInformation)
            peak = meter.GetPeakValue()
            if peak > threshold:
                active_sessions.append((session.Process.name(), peak))
        except Exception:
            continue
    return active_sessions


async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    
    if current_session:
        try:
            media_properties = await current_session.try_get_media_properties_async()
            playback_info = current_session.get_playback_info()
            # console.print(media_properties.thumbnail)
            info = {
                'title': media_properties.title or "Невідома назва",
                'artist': media_properties.artist or "Невідомий виконавець",
                'album': media_properties.album_title or "Невідомий альбом",
                'playback_status': playback_info.playback_status,
                'is_playing': playback_info.playback_status == 4,  # 4 = Playing
                'can_play': playback_info.controls.is_play_enabled,
                'can_pause': playback_info.controls.is_pause_enabled,
                'can_next': playback_info.controls.is_next_enabled,
                'can_previous': playback_info.controls.is_previous_enabled
            }
            return info
        except Exception as e:
            print(f"Помилка отримання інформації про медіа: {e}")
            return None
    return None


async def control_media(action):
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    
    if current_session:
        try:
            if action == 'play':
                await current_session.try_play_async()
            elif action == 'pause':
                await current_session.try_pause_async()
            elif action == 'next':
                await current_session.try_skip_next_async()
            elif action == 'previous':
                await current_session.try_skip_previous_async()
        except Exception as e:
            print(f"Помилка контролю медіа: {e}")
            return f"Помилка контролю медіа: {e}"
    return 'success'