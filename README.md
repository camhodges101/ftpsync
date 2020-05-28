# ftpsync

# Features that work
    1. Automatically syncs new files to file server to mirror client file structure
    2. GUI updates with state of sync script, GUI can be run and killed independantly to sync script
    3. Files that are deleted on client are archived on file server for recovered if needed
    4. Normal expected disconnects and file faults are handled. 
    5. client logging for troubleshooting
    6. Efficient transfer of duplicate files, duplicates are identified by SHA256 hash, duplicate files are only transferred once and then copied on file server
    7. All files have checksums (SHA256) to ensure they are transferred correctly without any missing data. 
    
# features to add
    1. File version tracking
    2. Change GUI updates from IP sockets to UDS.
    3. more efficient handling if files are moved to different directories (currrently they need to be retransferred instead of just moved on file server)
    4. Replace terminal GUI with web GUI
    5. multi client support (including mobile)