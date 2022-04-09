# -*- coding: utf-8 -*-
#NFS Hot Pursuit WII Texture noesis plugin by Allen
#Decode WII CMPR code by Zheneq https://github.com/Zheneq/Noesis-Plugins/blob/master/lib_zq_nintendo_tex.py

from inc_noesis import *
import lib_zq_nintendo_tex as nintex

def registerNoesisTypes():
    handle = noesis.register("NFS HotPursuitWii,Exient XGS Engine", ".twi")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = noeStrFromBytes(bs.readBytes(3))
    if idstring != "TWI":
        return 0
    return 1
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)
    idstring = bs.readInt()
    width = bs.readInt()
    height = bs.readInt()
    texUnk = bs.readInt()
    texFormat = bs.readInt()
    palFormat = bs.readInt()
    palDataSize = bs.readInt()
    pixelDataSize = bs.readInt()
    if(texFormat==4):
        print("4BPP PalFormat:",palFormat)
        palette = bs.readBytes(32)
        pixels = bs.readBytes(width*height//2)
        texture = nintex.convert(pixels, width, height, 8, palette, 2)
        texList.append(texture)  
    elif texFormat == 5:
        print("8BPP PalFormat:",palFormat)
        palette = bs.readBytes(512)
        pixels = bs.readBytes(width*height)
        texture = nintex.convert(pixels, width, height, 9 ,palette, 2)        
        texList.append(texture)
    elif texFormat == 250:
        print("16BPP RGB5A3")
        pixel = bs.readBytes(width*height*2)
        texture = nintex.convert(pixel, width, height, 5)
        texList.append(texture)        
    elif texFormat == 251:
        print("CMPR DXT1")
        pixel = bs.readBytes(width*height//2)
        texture = nintex.convert(pixel, width, height, 0xe)
        texList.append(texture)
    elif texFormat == 3:
        print("32BPP RGBA8")
        pixel = bs.readBytes(pixelDataSize)
        texture = nintex.convert(pixel, width, height, 6)
        texList.append(texture)
    elif texFormat == 12:
        print("8BPP I8")
        pixel = bs.readBytes(width*height)
        texture = nintex.convert(pixel, width, height, 1)
        texList.append(texture)        
    elif texFormat == 13:
        print("16BPP IA8")
        pixel = bs.readBytes(width*height*2)
        texture = nintex.convert(pixel, width, height, 3)
        texList.append(texture)
    elif texFormat == 0:
        print("16BPP rgb565")
        pixel = bs.readBytes(width*height*2)
        texture = nintex.convert(pixel, width, height, 4)
        texList.append(texture)        
    else:
        print("Unkonwn:",texFormat)
    return 1
