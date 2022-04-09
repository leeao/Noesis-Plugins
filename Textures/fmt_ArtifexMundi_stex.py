#Artifex Mundi .stex textures Importer Exporter Noesis plugin.
#Author: Allen
#2021-02-04
#Thanks Personperson for the compressed format information https://forum.xentax.com/viewtopic.php?f=33&t=22640 

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Artifex Mundi STEX Texture", ".stex")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
    noesis.addOption(handle, "-fmt", "\"-fmt <arg>\" support format: dxt1 dxt5 argb. default is argb",noesis.OPTFLAG_WANTARG)
    noesis.logPopup()
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readBytes(4)
        if idstring != b'\x53\x54\x45\x58':
                return 0
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()
        idstring = bs.readInt()         #0x58455453 STEX
        version = bs.readShort()
        minorVersion = bs.readShort()
        fileSize = bs.readUInt()
        const0x1C = bs.readInt()
        width = bs.readUShort()
        height = bs.readUShort()
        lz4Compressed = bs.readByte()
        texExtType = bs.readByte()      #2 = dds
        numMips = bs.readByte()
        unused = bs.readByte()
        fmtFourCC = bs.readUInt()
        compressSize = bs.readUInt()
        decompressSize = bs.readUInt()
        datas = bs.readBytes(compressSize)
        
        if lz4Compressed:
            datas = rapi.decompLZ4(datas,decompressSize)
            #rapi.exportArchiveFile("decmpdata.lz4",datas) #for test/check decompressed data.
            
        if fmtFourCC == 0x42475241: #ARGB                                 
            texture = NoeTexture(rapi.getInputName(), width, height, datas, noesis.NOESISTEX_RGBA32)
            texList.append(texture)  
        elif fmtFourCC == 0x35545844: #DXT5
            pixel = rapi.imageDecodeDXT(datas,width,height,noesis.NOESISTEX_DXT5)
            texture = NoeTexture(rapi.getInputName(), width, height, pixel, noesis.NOESISTEX_RGBA32)
            texList.append(texture)  
        elif fmtFourCC == 0x31545844: #DXT1
            pixel = rapi.imageDecodeDXT(datas,width,height,noesis.NOESISTEX_DXT1)
            texture = NoeTexture(rapi.getInputName(), width, height, pixel, noesis.NOESISTEX_RGBA32)
            texList.append(texture)              
        else:
            print("unknown format, can't support!")
            return 0
            
        return 1

def texWriteRGBA(data, width, height, bs):
        bs.writeUInt(0x58455453)
        bs.writeShort(1)        #version
        bs.writeShort(1)        #minor
        bs.writeInt(0)          #offset:0x8 filesize
        bs.writeInt(0x1C)       #const 0x1c
        bs.writeUShort(width)
        bs.writeUShort(height)
        bs.writeByte(0)         #lz4 compress flag
        bs.writeByte(2)         #texExtType
        bs.writeByte(1)         #num mipmap
        bs.writeByte(0)
        outData = data
        if noesis.optWasInvoked("-fmt"):
            fmt = noesis.optGetArg("-fmt")
            if fmt == "dxt5":
                bs.writeUInt(0x35545844)    #fmtFourCC "DXT5"
                outData = rapi.imageEncodeDXT(data,4,width,height,noesis.NOE_ENCODEDXT_BC3)
            elif fmt == "dxt1":
                bs.writeUInt(0x31545844)    #fmtFourCC "DXT1"
                outData = rapi.imageEncodeDXT(data,4,width,height,noesis.NOE_ENCODEDXT_BC1)
            elif fmt == "argb":
                bs.writeUInt(0x42475241)    #fmtFourCC "ARGB"
        else:        
            bs.writeUInt(0x42475241)        #fmtFourCC "ARGB"
        bs.writeUInt(len(outData))          #compressed data size. since lz4 Compressed flag is 0 so write data size.
        bs.writeUInt(len(outData))          #decompresed data size.
        bs.writeBytes(outData)
    
        fileSize = bs.tell()
        bs.seek(0x8)
        bs.writeUInt(fileSize)
        
        return 1
