#!/bin/bash

# /usr/local/bin/guglhupf-sync
{
    RECORDINGS_DIR=/mnt/recordings
    DRIVE_DIR=/guglhupf

    # Push missing files to Google Drive (without deleting locally removed files)
    /root/go/bin/drive push -quiet -files -no-prompt -exclude-ops "delete" "${RECORDINGS_DIR}${DRIVE_DIR}"

    # Delete uploaded files from local disk
    ALL_GDRIVE_FILES=`/root/go/bin/drive list -no-prompt -files "${RECORDINGS_DIR}${DRIVE_DIR}"`
    while IFS= read -r filename; do
        # If file exists locally, is present in Google Drive, and older than 60min,
        # delete it locally to free up space
        if [[ -f "${RECORDINGS_DIR}${filename}" && `stat --format=%Y "${RECORDINGS_DIR}${filename}"` -le $(( `date +%s` - 60*60 )) ]]; then
            rm "${RECORDINGS_DIR}${filename}"
        fi
    done <<< "$ALL_GDRIVE_FILES"

    # Save all uploaded files to text file
    /root/go/bin/drive list -no-prompt -files "${RECORDINGS_DIR}${DRIVE_DIR}" > "${RECORDINGS_DIR}/uploaded_files.txt"
} 2>&1 | tee -a /var/log/guglhupf-sync.log
