#by Allen
from inc_noesis import *
import struct
def registerNoesisTypes():
	handle = noesis.register("Manhunt 1 textures", ".txd")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
	noesis.logPopup()
	return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readInt()
        if idstring != 0x16:
                return 0
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()        
        while (bs.tell()<bs.getSize()):
                chunk=rwChunk(bs)
                if chunk.chunkID == 0x16:
                        rtex = rTex(bs.readBytes(chunk.chunkSize))
                        rtex.rTexList()
                        for t in rtex.texList:
                                texList.append(t)
                else:
                        bs.seek(chunk.chunkSize,1)
        return 1     


class rwChunk(object):   
        def __init__(self,bs):
                self.chunkID,self.chunkSize,self.chunkVersion = struct.unpack("3I", bs.readBytes(12))
class rTexNative(object):
        def __init__(self,datas):
                self.bs = NoeBitStream(datas)
        def rTexture(self):                
                texNativeStructHeader = rwChunk(self.bs)
                
                platformId = self.bs.readInt()
                textureFormat = self.bs.readInt()
                nameEndOfs = self.bs.tell()+32
                texName = self.bs.readString()
                self.bs.seek(nameEndOfs)
                self.bs.seek(32,1)

                rasterFormat = self.bs.readUInt()
                d3dFormat = self.bs.readUInt()
                width = self.bs.readUShort()
                height = self.bs.readUShort()
                depth = self.bs.readUByte()
                numLevels = self.bs.readUByte()
                rasterType = self.bs.readUByte()
                bitFlag = self.bs.readUByte()
                alpha = bitFlag & 0x1
                cubTeture = (bitFlag & 0x2) >> 1
                autoMipMaps = (bitFlag & 0x4) >> 2
                compressed = (bitFlag & 0x8) >> 3
                texFormatExt = rasterFormat & 0xf000
                texFormat = rasterFormat & 0xf00
                pixelBuffSize = self.bs.readUInt()
                pixelBuff = self.bs.readBytes(pixelBuffSize)
                if texFormat == 0x100:                  #DXT1 alpha                        
                        texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT1)           
                elif texFormat == 0x200:                  #DXT1 no alpha                        
                        texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT1)
                elif texFormat == 0x300:                #DXT3 alpha                        
                        texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT3)
                elif texFormat == 0x500:                #32bpp                         
                        texData = rapi.imageDecodeRaw(pixelBuff, width, height, "r8g8b8a8")
                elif texFormat == 0x600:                #24bpp                        
                        texData = rapi.imageDecodeRaw(pixelBuff, width, height, "r8g8b8p8")                        
                else:   
                        print("unknown format: ",texFormat)
                print("Format: ",texFormat,texName)
                texture = NoeTexture(texName, width, height, texData, noesis.NOESISTEX_RGBA32)
                return texture
class rTex(object):
        def __init__(self,datas):
                self.bs = NoeBitStream(datas)
                self.texList = []
                self.texCount = 0
        def rTexList(self):
                texStruct = rwChunk(self.bs)
                texCount = self.bs.readUShort()
                self.texCount = texCount
                deviceId = self.bs.readUShort()
                for i in range(texCount):
                        texNativeHeader = rwChunk(self.bs)
                        datas = self.bs.readBytes(texNativeHeader.chunkSize)
                        texNative = rTexNative(datas)
                        texture = texNative.rTexture()
                        self.texList.append(texture)
