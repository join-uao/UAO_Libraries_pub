## Description of library: 
This library is enabeling you to send infos to a cloud using your computer as a gateway.

## What type of library (SW/HW)
SW 

## Referenced libraries
SE.AppBase

How to use it : 
This is the block coming from the library :

  ![image](https://github.com/user-attachments/assets/770cc21a-9a31-4f42-97f7-01541c6bdd3d)

You will have to add some constant variables :
-CameraName -> Is the name of your object in the cloud.
-GatewayAddress -> This will be the IP address of your computer to send the data to the cloud.
>>ADP1 -> In this adapter the info you want to send to the cloud will be inside, in this adapter today 2 strings are possible to send.

When this three constant are set, deploy and running to the PLC, you can trigger the event to establish the connection with the cloud.
