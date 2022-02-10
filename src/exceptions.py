# Files exceptions -------------------
class FileDoesNotExist(Exception):
    pass


class RemoveFileFailed(Exception):
    pass


# Shazam exceptions ------------------
class TrackNotFound(Exception):
    pass


# Google Drive Exceptions --------------
class GoogleDriveClientSecretNotFound(Exception):
    pass


class GoogleDriveInvalidFileMeta(Exception):
    pass


class GoogleDriveUploadFail(Exception):
    pass


class GoogleDriveCreateFolderFail(Exception):
    pass


# Youtube exceptions -----------------
class YoutubeAudioDownloadFail(Exception):
    pass
