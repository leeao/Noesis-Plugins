# -*- coding: utf-8 -*-
#NFS Hot Pursuit WII Texture noesis plugin by Allen
#Indexed image untile code by wmltogether  https://github.com/wmltogether/FF12-Texture-Tool/blob/master/GIDecode.py
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
        tile_w= 8
        tile_h= 8
        palette = [rgb5a3(bs.readUShort()) for i in range(16)]
        #read 4bpp index as 8bpp
        pixel = [0]*(width*height)
        for i in range(width*height//2):
            index = bs.readByte()
            id1 = (index >> 4) & 0xf
            id2 = index & 0xf
            pixel[i*2] = id1
            pixel[i*2+1] = id2
        #other bytes is mipmap pixel bytes
        
        ntx = width//tile_w
        nty = height//tile_h
        newPixel = tile2linear(pixel,ntx,nty,tile_h,tile_w)
        newPixel = bytes(newPixel)
        textureData = bytearray(width * height * 4)
        for i in range(width * height):
            textureData[i * 4:(i + 1) * 4] = palette[newPixel[i]]
        texture = NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)  
    elif texFormat == 5:
        print("8BPP PalFormat:",palFormat)
        tile_w= 8
        tile_h= 4   
        palette = [rgb5a3(bs.readUShort()) for i in range(256)]
        pixel = bs.readBytes(pixelDataSize)
        if (width%tile_w):
            real_width = (width-(width%tile_w))+tile_w            
        else:
            real_width = width
        if (height%tile_h) :
            real_height = (height-(height%tile_h))+tile_h
        else:
            real_height = height
        ntx = real_width//tile_w
        nty = real_height//tile_h       
        newPixel = tile2linear(pixel,ntx,nty,tile_h,tile_w)
        newPixel = bytes(newPixel)
        textureData = bytearray(real_width * real_height * 4)
        for i in range(real_width * real_height):
            textureData[i * 4:(i + 1) * 4] = palette[newPixel[i]]
         
        if width != real_width or height != real_height:
            cutData = bytearray(width * height * 4)
            for y in range(height):
                oldIndex = y * real_width * 4
                newIndex = y * width *4
                cutData[newIndex:newIndex+width*4] = textureData[oldIndex:oldIndex+width*4]
            textureData = cutData
        texture = NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32)
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

def rgb5a3(rawPixel):
    t = bytearray(4)
    if rawPixel & 0x8000 != 0:  # r5g5b5
        t[0] = (((rawPixel >> 10) & 0x1F) * 0xFF // 0x1F)
        t[1] = (((rawPixel >> 5)  & 0x1F) * 0xFF // 0x1F)
        t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
        t[3] = 0xFF
    else:  # r4g4b4a3
        t[0] = (((rawPixel >> 8)  & 0x0F) * 0xFF // 0x0F)
        t[1] = (((rawPixel >> 4)  & 0x0F) * 0xFF // 0x0F)
        t[2] = (((rawPixel >> 0)  & 0x0F) * 0xFF // 0x0F)
        t[3] = (((rawPixel >> 12) & 0x07) * 0xFF // 0x07)
    return t
def tile2linear(data,ntx,nty,tile_h,tile_w):
    width=ntx*tile_w
    height=nty*tile_h
    tilelst=[]
    tile_len=tile_w*tile_h
    for k in range(0,width*height,tile_len):
        tile = data[k:k+tile_len]
        tilelst.append(tile)
    nPixel_data=[]
    for a in range(nty):
        for b in range(tile_h):
            for c in range(ntx):
                for d in range(tile_w):
                    index = a*ntx+c
                    index_tile = b*tile_w+d
                    nPixel_data.append((tilelst[index][index_tile]))
    return nPixel_data
