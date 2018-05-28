# BugTorrent

:books: Reti Peer To Peer - Università degli Studi di Ferrara :books:

A peer-to-peer server based on BitTorrent's approach:

> ### Smart Query flooding
> ### **Parallel parts**
>   * Focused on efficient fetching, not searching
>   * Preventing free-loading
>   * Divide large file into many pieces
>   * Allows simultaneous downloading
>
> ### Peers
>   * Peers login to a tracker in order to share and download a file
>
> ### Tracker
>   * Handle connected peers, giving infos about the file and who got the parts peers are interested in
>
> ### Chunks
>   * Solution to chunk request: random selection and rarest chunk first:
>      ** Avoid starvation when some peers depart
>      ** Avoid starvation across all peers wanting a file
>      ** Balance load by equalizing # of copies of chunks
>
> ### Free-riding
>   * Vast majority of users are free-riders (download and leave the system / limited bandwidth); solution:
>      ** Peer has limited upload bandwidth and must share it among multiple peers
>      ** Prioritizing the upload bandwidth
>      ** A few "peers" essentially act as servers
>      ** Allow the fastest peers to download from you and occasionally let some free loaders download

## Usage
```shell
python3 BugTorrent.py
```

**_Note:_** Python 3.6 or above is required

### Peer's supported commands:
[xxxB] = the parameter length in bytes
 
```shell

# Login
LOGI[4B].IPP2P[55B].PP2P[5B]
# Response will be
ALGI[4B].SessionID[16B]

# Add a file
ADDR[4B].SessionID[16B].LenFile[10B].LenPart[6B].Filename[100B].Filemd5[32B]
# Response will be
AADR[4B].#part[8B]

# Find a file
1) LOOK[4B].SessionID[16B].Ricerca[20B]
2) FCHU[4B].SessionID[16B].Filemd5[32B]
# Response will be
1) ALOO[4B].\#idmd5[3B].{Filemd5_i[32B].Filename_i[100B].LenFile[10B].LenPart[6B]}(i=1..\#idmd5)
2) AFCH[4B].\#hitpeer[3B].{IPP2P_i[55B].PP2P_i[5B].PartList_i[8bit][\#part8]}(i=1..\#hitpeer)

# Search a file
QUER[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]
# Response will be
AQUE[4B].Pktid[16B].IPP2P[55B].PP2P[5B].Filemd5[32B].Filename[100B]

# Download a file
1) RETP[4B].Filemd5[32B].PartNum[8B]
2) RPAD[4B].SessionID[16B].Filemd5[32B].PartNum[8B]
# Response will be
1) AREP[4B].\#chunk[6B].{Lenchunk_i[5B].data[LB]}(i=1..\#chunk)
2) APAD[4B].\#Part[8B]

# Logout
LOGO[4B].SessionID[16B]
# Response will be
1) NLOG[4B].\#partdown[10B]
2) ALOG[4B].\#partown[10B]

```

## Authors :rocket:
* [Federico Frigo](https://github.com/xBlue0)
* [Niccolò Fontana](https://github.com/NicFontana)
* [Giovanni Fiorini](https://github.com/GiovanniFiorini)
* [Marco Rambaldi](https://github.com/jhonrambo93)

Enjoy :sunglasses:
