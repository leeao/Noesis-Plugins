#RenderWare PSP TXD Textures Noesis Importer
#RenderWare Version 3.7.0.2 (0x1C020065)
#By Allen
             
from inc_noesis import *
import struct
def registerNoesisTypes():

	handle = noesis.register("RenderWare PSP Txd Textures", ".txd")
	noesis.setHandlerTypeCheck(handle, noepyCheckTypeTXD)
	noesis.setHandlerLoadRGBA(handle, txdLoadRGBA)    
	return 1
def noepyCheckTypeTXD(data):
    bs = NoeBitStream(data)
    idstring = bs.readUInt()
    if idstring != 0x16:
            return 0
    return 1
def txdLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    chunk = rwChunk(bs)
    if chunk.chunkID == 0x16:
            rtex = rTex(bs.readBytes(chunk.chunkSize))
            rtex.rTexList()  
            for j in range(len(rtex.texList)):
                texList.append(rtex.texList[j])      
    return 1
class rwChunk(object):   
        def __init__(self,bs):
                self.chunkID,self.chunkSize,self.chunkVersion = struct.unpack("3I", bs.readBytes(12))    
class rTex(object):
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
        self.texList = []
        self.texCount = 0
    def rTexList(self):
        texStruct = rwChunk(self.bs)
        texCount = self.bs.readUShort()
        self.texCount = texCount
        deviceId = self.bs.readUShort() # 1 for D3D8, 2 for D3D9, 6 for PlayStation 2, 8 for XBOX, 9 for PSP
        for i in range(texCount):
                texNativeHeader = rwChunk(self.bs)
                datas = self.bs.readBytes(texNativeHeader.chunkSize)
                if deviceId == 9:
                    texNative = rPSPTexNative(datas)                                   
                texture = texNative.rTexture()
                if texture != False:
                    self.texList.append(texture)    
class rPSPTexNative(object):
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
    def rTexture(self):                
        texNativeHeaderStruct = rwChunk(self.bs)    
        
        rasterFormat = self.bs.readUInt()
        width = self.bs.readUShort()
        height = self.bs.readUShort()
        depth = self.bs.readUByte()
        numLevels = self.bs.readUByte()
        rasterType = self.bs.readUByte()
        bitFlag = self.bs.readUByte()
        
        unkFlag = self.bs.readInt()
        self.bs.seek(76,NOESEEK_REL)
        unk1 = self.bs.readInt()
        unk2 = self.bs.readInt()        
        
        platformId = self.bs.readInt()
        textureFormat = self.bs.readInt()
        nameEndOfs = self.bs.tell()+32
        texName = self.bs.readString()
        self.bs.seek(nameEndOfs)
        self.bs.seek(32,1)

        
        texFormatExt = rasterFormat & 0xf000
        texFormat = rasterFormat & 0xf00
        pixelBuffSize = width * height * depth // 8
        texData = bytearray()
        
        if texFormatExt > 0:
            if texFormatExt == 0x2000:
                palette = self.bs.readBytes(1024)                    
            #elif texFormatExt == 0x4000:
            #    palette = self.bs.readBytes(64)
            #    self.bs.seek(64,1)#skip padding
            pixelBuff = self.bs.readBytes(pixelBuffSize)
            if depth == 8:                           
                pixelBuff = rapi.imageUntwiddlePSP(pixelBuff,width,height,8)
                texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 8, "r8g8b8a8")                                            
            #elif depth == 4:
            #    pixelBuff = rapi.imageUntwiddlePSP(pixelBuff,width,height,4)
            #    texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 4, "r8g8b8a8")               
        ext = rwChunk(self.bs) 
        if ext.chunkSize > 0:
            self.bs.seek(ext.chunkSize,NOESEEK_REL)                
        if len(texData) > 0:                             
            texture = NoeTexture(texName, width, height, texData, noesis.NOESISTEX_RGBA32)
        else:
            return False
        return texture         