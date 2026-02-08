# Supported IR formats:

## Remotecentral.com:
URL: https://www.remotecentral.com/cgi-bin/codes/
RemoteCentral files only contains individual raw codes (per function/key). Therefore, the data must be enriched beforehand.
*Example:*
**Poweroff:**

    0000 006d 0000 0020 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 06d2 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 001e 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 06d2

**Poweron:**

    0000 006d 0000 0020 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 06d2 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 06d2

Must be converted in the following order:
*file_name.ir:*

    Filetype: IR signals file
    Version: 1
    #
    #RemoteCentral:Denon:AVR-3801 
    #
    PowerOff
    0000 006d 0000 0020 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 06d2 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 001e 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 06d2
    Power On
    0000 006d 0000 0020 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 06d2 000a 001e 000a 0046 000a 001e 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 0046 000a 0046 000a 001e 000a 001e 000a 001e 000a 0046 000a 0046 000a 06d2


## Flipper
URL https://github.com/Lucaslhm/Flipper-IRDB
Flipper files can be imported directly (in raw format).

To do this, either go to the "*raw*" module in the file and copy and paste the data into a local file.
*Or load it directly from Flipper URL:*
**Example**:

    https://github.com/Lucaslhm/Flipper-IRDB/blob/main/Audio_and_Video_Receivers/Denon/Denon_AVR_Receiver.ir

Add `?raw=true` to the end of the URL. So:

    https://github.com/Lucaslhm/Flipper-IRDB/blob/main/Audio_and_Video_Receivers/Denon/Denon_AVR_Receiver.ir?raw=true

## IRDB
URL https://github.com/probonopd/irdb/tree/master/codes
IRDB files can be imported directly (in raw format).

To do this, either go to the "*raw*" module in the file and copy and paste the data into a local file.
*Or load it directly from IRDB:*
**Example**:

    https://github.com/probonopd/irdb/blob/master/codes/ADB/Set%20Top%20Box/42%2C17.csv

Add `?raw=true` to the end of the URL, so:

    https://github.com/probonopd/irdb/blob/master/codes/ADB/Set%20Top%20Box/42%2C17.csv?raw=true

