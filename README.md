# VaultOs
A prototype Custom Rom for the SHIFTphone 8 that aims to deliver absurdly high security demands—using air-gapping—to block even state-sponsored tojans like Pegasus.


This repo is a Fork of   
https://github.com/LineageOS/android_device_shift_otter  
Full credit belongs to the original creators, and the code remains entirely theirs.  
A big thanks goes to the lineage os and shift team for creating so nice to work with software!  
To use git lfs we had to remove the official fork connection.  

# About
There are minor further optimizations and primarly added other open source Apps flashed with the ROMs.  
The ROM has fully disabled Wifi, Modem and USB-C Datatraffic within its kernel. Which means you are no longer able to use adb even in recovery same for transfer files. (See [Recover](#recover) to switch back to other roms)  


Bluetooth is dangerous as well but a more local danger so it is up to the user to consider using it or not. You might want to have a look at   
CVE-2025-0084   
CVE-2015-6602 (aka Stagefright)  
CVE-2020-0022 (BlueFrag)  


The Rom comes with Briar preinstalled and it is proven to work as an air gapped messenger.
So you need two devices, a regular everyday device with internet and a VaultOs device.   
Both devices run briar setup and connect either via bluetooth (unsecure but convenient) or sd card (very secure but inconvinient). Contacts need to know the VaultOs devices Briar Id and send the messages via the daily use device with TOR support.  
Briar can be used on non VaultOs devices as well but obviously arent protected for Pegasus and similar products in that case.  


For more information see:  
https://github.com/briar/briar  


In far future there might be a little more handy air gapped messenger apps e.g. see or support  
https://github.com/Hatzen/ParAnnoying-Releases

## Full (planned) Features

- Airgap WIFI, Modem, USB-C via Kernel (
https://github.com/Hatzen/android_kernel_shift_qcm6490)
- Killswitch to factory reset if connection is detected again
    - (NOTE: SD Cards cant be wiped properly and data may be recovered with goverment like abilities and resources; Still not very probable)
- messengers that can work in air gapped mode e.g. Briar
- Utilisation of the Custom Key, to extract all text from screen and copy it to clipboard
- offline wiki via Kiwix
- Full office suite e.g. Libreoffice
- Offline Maps and GPS
- Root and Terminal via KernelSU and Termux
- Backups via Neobackup
- Movie Support via VLC
- Dashcam via Alibi
- Sandbox APKs via Insular
- Offline AI

## Installtion

WARNING: Be careful the process may Brick your phone if anything is done wrong.  


Download the zip and flash it via fastboot or recovery.  
See e.g. https://forum.shiftphones.com/threads/  shiftphone-8-crdroid-12-11-unofficial-android-16qpr2.7744/#-installation  
The image is currently an unsigned userbuild which needs to keept the bootloader open and disabled verification. In future milestones the bootloader will be lockable as shift is supports this nicely.

### Recover 
You need to boot into bootloader and then run the commands  


fastboot flash boot boot.img  
fastboot flash vendor_boot vendor_boot.img  
fastboot flash dtbo dtbo.img  


e.g. from the stock rom or an lineage os build. See  
https://downloads.shiftphones.com/public/SP8/release/OTTER.SOS.6.7.G-RELEASE-20260712/

## Why (only for) Shiftphone?

It would be possible to support other devices as well but there are only a few thousand people how really would need this kind of software and suppporting more devices is time consuming.  
And the Shiftphone 8 has already two Hardware Killswitches for Camera and Microphone. 
And espacially the repairability is quiet good, you may be able to bring the device up again without needing to wipe the internal SD Card.   
Furthermore the custom rom community is great and security patches are delivered reliable and the device is build to last the next 10 years. Its focus on fair build processes for medium hardware are a reason to support it as well.  

## Why using it at all?

Currently not a single of the popular Messengers like Signal, Telegram, Whatsapp, Threema can protect you against trojans like pegasus which potentialy get installed at any time from anywhere and can read everything when decrypted like they see your whole screen the whole time.  


You can use any device and stock rom and just enable airplane mode to cut off connections, but when devices get connection at any time the device might get infected by a trojan which may disable airplane mode without it being visible so hardware disabled roms and kill switches which factory reset your device on connection detection may be useful.  


Futhermore it is an educational project for me to get in touch with android os builds and security topics.  

### Political

The normal everyday day user does not need this state of security or parannoying stuff. But there is evidence of people who get surveiled just because they are inconvenient.  
https://en.wikipedia.org/wiki/Pegasus_(spyware)#Use_against_Spanish_government_officials  
https://en.wikipedia.org/wiki/Pegasus_(spyware)#Germany  


Some countries block there users to talk to people in other countries e.g. north korea or saudi arabia, these countries wont allow this sort of software but still it might be used if it would be legal.  

Tragic history shows that a select few may critically need this kind of software  
in honor of   
[Jamal Khashoggi](https://en.wikipedia.org/wiki/Jamal_Khashoggi#The_Washington_Post)  
[Cecilio Pineda Birto](https://en.wikipedia.org/wiki/Pegasus_(spyware)#Mexico)  
and everyone being persued or pressured for keeping their opinion.  

# Legal Advice

Even though the Software is intended to defend against survaillance it is not intended to be used for crimes in any way.  
It should enforce privacy rights and defend peoples free will and mind.  


None of the authors of foreign software utilized in this repo is responsible for the product, usage and connotation or dangers coming from this software.  


This software is just a prototype there is no warranty or guarantee for any harm to hardware, data or failed security introduced by this software.  

# App Sources

TODO: Fully list and give credits to each foreign source  

