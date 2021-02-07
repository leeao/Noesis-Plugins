#RenderWare DFF Models and TXD Textures Noesis Importer
#RenderWare Version 3.7.0.2 (0x1C020065)
#By Allen(Leeao)
'''
Support games:
    Manhunt [PC]
    Agent Hugo [PC]
    Silent Hill Origins [PS2]
    Mortal Kombat Deadly Alliance [PS2]
    Mortal Kombat Deception [PS2]
    Mortal Kombat Armageddon [PS2]
'''                
from inc_noesis import *
import struct
def registerNoesisTypes():
	handle = noesis.register("RenderWare PS2/PC DFF Models", ".dff;.rws")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, dffLoadModel)
	handle = noesis.register("RenderWare PS2/PC Txd Textures", ".txd")
	noesis.setHandlerTypeCheck(handle, noepyCheckTypeTXD)
	noesis.setHandlerLoadRGBA(handle, txdLoadRGBA)    
	return 1
def noepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = bs.readUInt()
    bs.seek(8)
    idstring2 = bs.readUInt()
    if idstring not in (0x10,0x24) and idstring2 != 0x10 :
            return 0
    return 1
def noepyCheckTypeTXD(data):
    bs = NoeBitStream(data)
    idstring = bs.readUInt()
    if idstring not in (0x16,0x23):
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
    elif chunk.chunkID == 0x23:
            texDict = rTexDict(bs.readBytes(chunk.chunkSize))
            texDict.read()
            for j in range(len(texDict.texList)):
                texList.append(texDict.texList[j])
    return 1
isMKPS2 = 0
def dffLoadModel(data, mdlList):
    global isMKPS2
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()        
    fileSize = len(data)
    bs.seek(8)
    checkMKPS2 = bs.readUInt()
    if checkMKPS2 == 0x10:
        isMKPS2 = 1
        fileSize = bs.tell() + bs.readUInt() + 8
        bs.seek(8)
    else:
        bs.seek(0)
    while(bs.tell() < fileSize):
        chunk = rwChunk(bs)
        if chunk.chunkID == 0x10:                
                datas = bs.readBytes(chunk.chunkSize)
                clump = rClump(datas)
                clump.readClump()
                if len(clump.mdlList) > 0:
                    mdlList.append(clump.mdlList[0])
        else:
                bs.seek(chunk.chunkSize,1)
    return 1
class rwChunk(object):   
        def __init__(self,bs):
                self.chunkID,self.chunkSize,self.chunkVersion = struct.unpack("3I", bs.readBytes(12))
def readRWString(bs):
    rwStrChunk = rwChunk(bs)
    endOfs = bs.tell() + rwStrChunk.chunkSize
    string = bs.readString()   
    bs.seek(endOfs)
    return string
class rD3D8TexNative(object):
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
        dirName = rapi.getDirForFilePath(rapi.getInputName())
        outName = dirName + texName + ".png"                
        noesis.saveImageRGBA(outName,texture)                
        return texture      
class rPS2TexNative(object):
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
    def rTexture(self):                
        texNativeHeaderStruct = rwChunk(self.bs)                
        platformId = self.bs.readInt()
        textureFormat = self.bs.readInt()
        texName = readRWString(self.bs)
        maskName = readRWString(self.bs)
        
        nativeStruct = rwChunk(self.bs)                
        rasterStruct = rwChunk(self.bs)                                
        width = self.bs.readUInt()
        height = self.bs.readUInt()
        depth = self.bs.readUInt()
        rasterFormat = self.bs.readUInt()
        TEX0_GS_REGISTER = self.bs.readUInt64()
        TEX1_GS_REGISTER = self.bs.readUInt64()
        MIPTBP1_GS_REGISTER = self.bs.readUInt64()
        MIPTBP2_GS_REGISTER = self.bs.readUInt64()
        texelDataSectionSize = self.bs.readUInt()
        paletteDataSectionSize = self.bs.readUInt()
        gpuDataAlignedSize = self.bs.readUInt()
        skyMipmapVal = self.bs.readUInt()
        
        texStruct = rwChunk(self.bs)
        
        texFormatExt = rasterFormat & 0xf000
        texFormat = rasterFormat & 0xf00
        pixelBuffSize = texelDataSectionSize - 80
        palltetBuffSize = paletteDataSectionSize - 80
        self.bs.seek(80,NOESEEK_REL) #skip TexPixelHeader
        pixelBuff = self.bs.readBytes(pixelBuffSize)
        self.bs.seek(80,NOESEEK_REL) #skip TexPalleteHeader
        if texFormatExt == 0x2000:
                palette = readPS2Palette(self.bs,256)                     
        elif texFormatExt == 0x4000:
                palette = readPS2Palette(self.bs,16)                       
                self.bs.seek((palltetBuffSize - 64),1)#skip padding
        ext = rwChunk(self.bs) 
        self.bs.seek(ext.chunkSize,NOESEEK_REL)                
        if depth == 8:
            #pixelBuff = rapi.imageUntwiddlePS2(pixelBuff,width,height,8)
            #texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 8, "r8g8b8a8",noesis.DECODEFLAG_PS2SHIFT)                        
            pixelBuff = unswizzle8(pixelBuff,width,height)
            palette = unswizzlePalette(palette)
            texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 8, "r8g8b8a8")                                            
        elif depth == 4:
            pixelBuff = unswizzle4(pixelBuff, width, height)
            texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 4, "r8g8b8a8")                               
        dirName = rapi.getDirForFilePath(rapi.getInputName())
        outName = dirName + texName + ".png"                
        texture = NoeTexture(texName, width, height, texData, noesis.NOESISTEX_RGBA32)
        noesis.saveImageRGBA(outName,texture)
        return texture
def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t                  
def readPS2Palette(bs,numColor):
    palette = bytes()
    for i in range(numColor):
        palette += rgba32(bs.readUInt()) 
    return palette
def unswizzlePalette(palBuffer):  
    newPal = bytearray(1024)     
    for p in range(256):
        pos = ((p & 231) + ((p & 8) << 1) + ((p & 16) >> 1)) 
        newPal[pos*4:pos*4+4] = palBuffer[p*4:p*4+4]
    return newPal
def unswizzle8(buf,width,height):
    out = bytearray(width*height)
    for y in range(height):
        for x in range(width):
            block_location = (y & (~0xf)) * width + (x & (~0xf)) * 2
            swap_selector = (((y + 2) >> 2) & 0x1) * 4
            posY = (((y & (~3)) >> 1) + (y & 1)) & 0x7
            column_location = posY * width * 2 + ((x + swap_selector) & 0x7) * 4
            byte_num = ((y >> 1) & 1) + ((x >> 2) & 2)
            swizzleid = block_location + column_location + byte_num
            out[y * width + x] = buf[swizzleid]
    return out   
def unswizzle4(buffer, width, height):    
    pixels = bytearray(width * height)
    for i in range(width*height//2):
        index = buffer[i]
        id2 = (index >> 4) & 0xf
        id1 = index & 0xf
        pixels[i*2] = id1
        pixels[i*2+1] = id2
    newPixels = unswizzle8(pixels,width,height)    
    result = bytearray(width * height)
    for i in range(width*height//2):
            idx1 = newPixels[i*2+0]
            idx2 = newPixels[i*2+1]
            idx = ((idx2 << 4) | idx1) & 0xff
            result[i] = idx        
    return result                 
class rTex(object):
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
        self.texList = []
        self.texCount = 0
    def rTexList(self):
        texStruct = rwChunk(self.bs)
        texCount = self.bs.readUShort()
        self.texCount = texCount
        deviceId = self.bs.readUShort() # 1 for D3D8, 2 for D3D9, 6 for PlayStation 2, 8 for XBOX
        for i in range(texCount):
                texNativeHeader = rwChunk(self.bs)
                datas = self.bs.readBytes(texNativeHeader.chunkSize)
                if deviceId == 1:
                    texNative = rD3D8TexNative(datas)
                elif deviceId == 6:
                    texNative = rPS2TexNative(datas)
                texture = texNative.rTexture()
                self.texList.append(texture)
def rTexture(bs):
    texHeader = rwChunk(bs)
    texStructHeader = rwChunk(bs)
    textureFilter = bs.readByte()
    UVAddressing = bs.readByte()
    useMipLevelFlag = bs.readShort()
    texName = noeStrFromBytes(bs.readBytes(rwChunk(bs).chunkSize))
    bs.seek(rwChunk(bs).chunkSize,1)
    texExtHeader = rwChunk(bs)
    bs.seek(texExtHeader.chunkSize,1)
    return texName
class rImage(object):     
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
    def read(self):
        imageStruct = rwChunk(self.bs)
        width = self.bs.readUInt()
        height = self.bs.readUInt()
        depth = self.bs.readUInt()
        pitch = self.bs.readUInt()
        pixelSize = pitch * height
        real_width = pixelSize * 8 // depth // height
        pixel = self.bs.readBytes(pixelSize)
        pixel = crop(pixel,real_width,height,width,height,depth)        
        if depth == 8:
            palette = self.bs.readBytes(1024)
            textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r8g8b8a8")         
        elif depth == 32:
            textureData = pixel
        else:
            print("can't support this format:",depth)
            return 0
        return (NoeTexture("tex", width, height, textureData, noesis.NOESISTEX_RGBA32))      
class rTexDict(object):
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
        self.texList = []
        self.texCount = 0
    def read(self):
        self.texCount = self.bs.readUShort()
        deviceId = self.bs.readUShort() # 1 for D3D8
        for i in range(self.texCount):
            numMips = self.bs.readUInt()
            for j in range(numMips):
                imageHeader = rwChunk(self.bs)
                datas = self.bs.readBytes(imageHeader.chunkSize)
                #only top level mipmap
                if j == 0:
                    image = rImage(datas)
                    texture = image.read()                       
            texName = rTexture(self.bs)
            if texture:
                texture.name = texName
                self.texList.append(texture)
                dirName = rapi.getDirForFilePath(rapi.getInputName())
                outName = dirName + texName + ".png"                
                noesis.saveImageRGBA(outName,texture)                
def crop(pixel,real_width,real_height,cropWidth,cropHeight,bpp):
    #Note: this function can't apply to 4bpp
    #for 4bpp: first convert 4bpp to 8bpp then run this function
    #Because some 4bpp array sizes are not integers.
    if real_width == cropWidth and real_height == cropHeight:
        return pixel
    minWidth = min(real_width,cropWidth)
    minHeight = min(real_height,cropHeight)
    length = cropWidth * cropHeight * bpp // 8 
    outPixel = bytearray(length)    
    dstLineSize = minWidth * bpp // 8
    srcLineSize = real_width * bpp // 8

    for y in range(minHeight):        
        dstIndex = y * dstLineSize
        srcIndex = y * srcLineSize
        outPixel[dstIndex:dstIndex+dstLineSize] = pixel[srcIndex:srcIndex+dstLineSize]
    return outPixel            
class rClump(object):
        def __init__(self,datas):
            self.bs = NoeBitStream(datas)
            self.mdlList = []
        def readClump(self):     
            rapi.rpgReset()         
            clumpStructHeader = rClumpStruct(self.bs)            
            framtListHeader = rwChunk(self.bs)
            datas = self.bs.readBytes(framtListHeader.chunkSize)
            frameList = rFrameList(datas)
            bones = frameList.readBoneList()
            skinBones = frameList.getSkinBones()
            geometryListHeader = rwChunk(self.bs)
            geometryListStructHeader = rwChunk(self.bs)
            geometryCount = self.bs.readUInt()
            if geometryCount:
                    datas = self.bs.readBytes(geometryListHeader.chunkSize-16)
            vertMatList=[0]*clumpStructHeader.numAtomics
            if clumpStructHeader.numAtomics:
                    atomicData = bytes()
                    for i in range(clumpStructHeader.numAtomics):
                            atomicHeader = rwChunk(self.bs)
                            atomicData += self.bs.readBytes(atomicHeader.chunkSize)
                    atomicList = rAtomicList(atomicData,clumpStructHeader.numAtomics).rAtomicStuct()
                    for j in range(clumpStructHeader.numAtomics):
                            vertMatList[atomicList[j].geometryIndex]= bones[atomicList[j].frameIndex].getMatrix()
            if geometryCount:
                    geometryList = rGeometryList(datas,geometryCount,vertMatList)
                    geometryList.readGeometry()                                
                    mdl = rapi.rpgConstructModel()
                    
                    texList = []  
                    texNameList = []
                    existTexNameList = []
                    path = rapi.getDirForFilePath(rapi.getInputName())
                    for m in range(len(geometryList.matList)):
                        texName = geometryList.matList[m].name
                        if texName not in texNameList:
                            texNameList.append(texName)                        
                            fullTexName = path+texName+".png"
                            if rapi.checkFileExists(fullTexName):            
                                texture = noesis.loadImageRGBA(fullTexName)
                                texList.append(texture)
                                existTexNameList.append(texName)
                    
                    matList = []
                    for i in range(len(texList)):
                            matName = existTexNameList[i]
                            material = NoeMaterial(matName, texList[i].name)
                            #material.setDefaultBlend(0)
                            matList.append(material)                    
                    mdl.setModelMaterials(NoeModelMaterials(texList,matList))
                    mdl.setBones(skinBones)
                    self.mdlList.append(mdl)
                    #rapi.rpgReset()  
            else:
                   mdl = NoeModel()
                   mdl.setBones(bones)
                   self.mdlList.append(mdl) 
class rClumpStruct(object):
        def __init__(self,bs):
                self.chunkID,self.chunkSize,self.chunkVersion = struct.unpack("3I", bs.readBytes(12))                
                self.numAtomics = bs.readUInt()
                self.numLights = bs.readUInt()
                self.numCameras = bs.readUInt()
class rFrameList(object):
        def __init__(self,datas):
                self.bs = NoeBitStream(datas)                
                self.frameCount = 0
                self.boneMatList=[]
                self.bonePrtIdList=[]
                self.boneIndexList=[]
                self.animBoneIDList=[]
                self.boneNameList=[]                
                self.hAnimBoneIDList =[]
                self.hSkinBoneIDList=[]                
                self.bones = []
                self.skinBones=[]
                self.hasHAnim = 0
                self.hasBoneName = 0
        def rFrameListStruct(self):
                header = rwChunk(self.bs)
                frameCount = self.bs.readUInt()
                self.frameCount = frameCount
                if frameCount:
                        for i in range(frameCount):
                                boneMat = NoeMat43.fromBytes(self.bs.readBytes(48)).transpose()
                                bonePrtId = self.bs.readInt()
                                self.bs.readInt()
                                self.boneMatList.append(boneMat)
                                self.bonePrtIdList.append(bonePrtId)
                                self.boneIndexList.append(i)

        def rHAnimPLG(self):
                hAnimVersion = self.bs.readInt()
                self.animBoneIDList.append(self.bs.readInt())
                boneCount = self.bs.readUInt()
                if boneCount:
                        self.hasHAnim = 1
                        flags = self.bs.readInt()
                        keyFrameSize = self.bs.readInt()
                        for i in range(boneCount):
                                if not isMKPS2:
                                    self.hAnimBoneIDList.append(self.bs.readInt())
                                else:
                                    value = self.bs.readInt()
                                    self.hAnimBoneIDList.append(value & 0xffff)
                                self.hSkinBoneIDList.append(self.bs.readInt())
                                boneType = self.bs.readInt()
        def rUserDataPLG(self,index):
                numSet = self.bs.readInt()
                boneName = "Bone"+str(index)
                for i in range(numSet):
                        typeNameLen = self.bs.readInt()
                        self.bs.seek(typeNameLen,1)
                        u2 = self.bs.readInt()
                        u3 = self.bs.readInt()
                        boneNameLen = self.bs.readInt()
                        if boneNameLen>1:
                                boneName = self.bs.readString()
                self.boneNameList.append(boneName)
        def rFrameName(self,nameLength):
                boneName = ""
                boneNameBytes = self.bs.readBytes(nameLength);
                boneName = str(boneNameBytes, encoding = "utf-8")
                return boneName
        def rFrameExt(self,index):
                header = rwChunk(self.bs)
                endOfs = self.bs.tell() + header.chunkSize
                hasName = 0
                if header.chunkSize:
                        while (self.bs.tell()<endOfs):
                                chunk = rwChunk(self.bs)                                
                                if chunk.chunkID == 0x11e:
                                        self.rHAnimPLG()
                                elif chunk.chunkID == 0x253F2FE:  
                                        hasName = 1
                                        self.boneNameList.append(self.rFrameName(chunk.chunkSize))
                                        if self.hasBoneName != 1:
                                            self.hasBoneName = 1
                                elif chunk.chunkID == 0x11f:
                                        hasName = 1
                                        self.rUserDataPLG(index)
                                        if self.hasBoneName != 1:
                                            self.hasBoneName = 1
                                else:
                                        self.bs.seek(chunk.chunkSize,1)
                if(hasName==0):
                        if index==1:
                                self.boneNameList.append("RootBone")
                        else:
                                self.boneNameList.append("Bone"+str(index))
        def rFrameExtList(self):
                for i in range(self.frameCount):
                        self.rFrameExt(i)
        
        def readBoneList(self):
                self.rFrameListStruct()
                self.rFrameExtList()
                #Just list order
                bones=[]
                for i in range(self.frameCount):
                        boneIndex = i
                        boneName = self.boneNameList[i]
                        boneMat = self.boneMatList[i]
                        bonePIndex = self.bonePrtIdList[i]
                        bone = NoeBone(boneIndex, boneName, boneMat, None, bonePIndex)
                        bones.append(bone)
                        
                for i in range(self.frameCount):
                        bonePIndex = self.bonePrtIdList[i]
                        if(bonePIndex>-1):
                                prtMat=bones[bonePIndex].getMatrix()
                                boneMat = bones[i].getMatrix()                             
                                bones[i].setMatrix(boneMat * prtMat)
                self.bones = bones
                return bones
        def getSkinBones(self):      
                #编程思路
                #通过比较每个骨骼的AnimBoneID 和 hAnimBoneIDList 里面的 AnimBoneID 是否相同. AnimBoneID需要大于>0.
                #然后得到一个存在的AnimBoneID数组，SkinBoneID数组（未从0排序），frameListID数组（数组存储顺序ID，方便访问父级和名称，矩阵），父级骨骼ListID数组
                #通过遍历父级骨骼ListID数组，查看是否和frameListID数组相同，然后得到父级的SkinBoneID。链接父级。
                #根据skinBoneID从0开始重新排序. 本步骤不是必做，因为Noesis自动矫正列表,不过还是做了。
                if self.hasHAnim > 0: 
                    boneDataList = []
                    for i in range(len(self.animBoneIDList)):
                        index = i
                        if len(self.animBoneIDList) == (self.frameCount - 1):
                            index = i + 1
                        elif len(self.animBoneIDList) == self.frameCount:
                            index = i                            
                        curBoneAnimBoneID = self.animBoneIDList[i]
                        if curBoneAnimBoneID > 0:
                            for j in range(len(self.hAnimBoneIDList)):
                                if curBoneAnimBoneID == self.hAnimBoneIDList[j]:
                                    boneData = skinBone()
                                    if self.hasBoneName == 1:
                                        boneData.boneName = self.boneNameList[index]
                                    else:                            
                                        boneData.boneName = "Bone" + str(curBoneAnimBoneID)
                                    boneData.matrix = self.bones[index].getMatrix()
                                    boneData.skinBoneID = self.hSkinBoneIDList[j]
                                    boneData.animBoneID = curBoneAnimBoneID
                                    boneData.listID = index
                                    boneData.listParentID = self.bonePrtIdList[index]
                                    boneDataList.append(boneData)
                    #find parent skin bone id
                    for i in range(len(boneDataList)):
                        for j in range(len(boneDataList)):
                            if boneDataList[i].listParentID == boneDataList[j].listID:
                                boneDataList[i].skinBoneParentID = boneDataList[j].skinBoneID
                            if len(self.animBoneIDList) == (self.frameCount - 1):
                                if boneDataList[i].listParentID == 0 :
                                    boneDataList[i].skinBoneParentID = -1
                                
                    bones = [0] * len(boneDataList)
                    #bones = []
                    for j in range(len(boneDataList)):                
                            boneIndex = boneDataList[j].skinBoneID
                            boneName =  boneDataList[j].boneName
                            boneMat = boneDataList[j].matrix
                            bonePIndex = boneDataList[j].skinBoneParentID
                            bone = NoeBone(boneIndex, boneName, boneMat, None,bonePIndex)
                            #bones.append(bone)    
                            bones[boneIndex] = bone

                    self.skinBones = bones                   
                else:
                    bones = self.bones       
                return bones
class skinBone(object):
        def __init__(self):
            #self.bone = 0
            self.boneName = 0
            self.matrix = 0
            self.skinBoneID = 0
            self.animBoneID = 0
            self.skinBoneParentID = 0
            self.listID = 0
            self.listParentID = 0
            
class Atomic(object):
        def __init__(self):
               self.frameIndex = 0
               self.geometryIndex = 0
class rAtomicList(object):
        def __init__(self,datas,numAtomics):
               self.bs = NoeBitStream(datas)
               self.numAtomics = numAtomics
        def rAtomicStuct(self):
                atomicList=[]
                for i in range(self.numAtomics):
                        header = rwChunk(self.bs)
                        atomic = Atomic()
                        atomic.frameIndex = self.bs.readUInt()
                        atomic.geometryIndex = self.bs.readUInt()
                        flags = self.bs.readUInt()
                        unused = self.bs.readUInt()
                        extHeader = rwChunk(self.bs)
                        self.bs.seek(extHeader.chunkSize,1)
                        atomicList.append(atomic)
                return atomicList
                 
class rMatrial(object):
        def __init__(self,datas):
                self.bs = NoeBitStream(datas)   
                self.skinUsedBoneIDList = []
                self.diffuseColor = NoeVec4([1.0, 1.0, 1.0, 1.0])
        def rMaterialStruct(self):
                header = rwChunk(self.bs)
                unused = self.bs.readInt()
                colorR = self.bs.readUByte()
                colorG = self.bs.readUByte() 
                colorB = self.bs.readUByte()
                colorA = self.bs.readUByte()
                self.diffuseColor = NoeVec4([colorR, colorG, colorB, colorA])
                unused2 = self.bs.readInt()
                hasTexture = self.bs.readInt()
                ambient = self.bs.readFloat()
                specular = self.bs.readFloat()
                diffuse = self.bs.readFloat()
                texName = ""
                if hasTexture:
                        texHeader = rwChunk(self.bs)
                        texStructHeader = rwChunk(self.bs)
                        textureFilter = self.bs.readByte()
                        UVAddressing = self.bs.readByte()
                        useMipLevelFlag = self.bs.readShort()
                        texName = noeStrFromBytes(self.bs.readBytes(rwChunk(self.bs).chunkSize))
                        #alphaTexName = noeStrFromBytes(self.bs.readBytes(rwChunk(self.bs).chunkSize))
                        self.bs.seek(rwChunk(self.bs).chunkSize,1)
                        texExtHeader = rwChunk(self.bs)
                        self.bs.seek(texExtHeader.chunkSize,1)
                matExtHeader = rwChunk(self.bs)
                #self.bs.seek(matExtHeader.chunkSize,1)
                matExtEndOfs = self.bs.tell() + matExtHeader.chunkSize;
                if matExtHeader.chunkSize > 0:
                    while self.bs.tell() < matExtEndOfs:
                        chunk = rwChunk(self.bs)
                        if chunk.chunkID == 0x895303:
                            self.rMKPS2SkinUsedBoneIDList()
                        else:
                            self.bs.seek(chunk.chunkSize,NOESEEK_REL)                    
                return texName
        def rMKPS2SkinUsedBoneIDList(self):
                unk1  = self.bs.readUShort()
                dataType  = self.bs.readUShort() #0xE000 0x6000 use for skin model , 0x0 is no skin.
                unk2  = self.bs.readInt()
                unk3  = self.bs.readFloat()
                if dataType > 0:
                    numBoneIDs = self.bs.readInt()
                    for i in range(numBoneIDs):
                        self.skinUsedBoneIDList.append(self.bs.readInt())
                unk4 = self.bs.readInt()
                unk5 = self.bs.readFloat()
                if dataType == 0xE000:
                    self.bs.seek(16,NOESEEK_REL)
                unk6 = self.bs.readInt()
                unk7 = self.bs.readInt()
class rMaterialList(object):
        def __init__(self,datas):
                self.bs = NoeBitStream(datas)            
                self.matCount = 0
                self.matList = []
                self.texList = []
                self.skinUsedBoneIDList = []
        def rMaterialListStruct(self):
                header = rwChunk(self.bs)
                self.matCount = self.bs.readUInt()
                self.bs.seek(self.matCount*4,1)
        def getMaterial(self):
                self.rMaterialListStruct()
                for i in range(self.matCount):
                        matData = self.bs.readBytes(rwChunk(self.bs).chunkSize)
                        mat = rMatrial(matData)
                        texName = mat.rMaterialStruct()                          
                        self.texList.append(texName)
                        if texName != "":                            
                            #matName = "material[%d]" %len(self.matList)
                            matName = texName
                            #matName = "mtl"+str(i)
                            material = NoeMaterial(matName, texName)
                            material.setDefaultBlend(0)
                            self.matList.append(material)                            
                        else:                            
                            matName = "mtl"+str(i)
                            material = NoeMaterial(matName, None)
                            material.setDiffuseColor(mat.diffuseColor)                            
                            self.matList.append(material)                            
                        #texture = NoeTexture()                        
                        if len(mat.skinUsedBoneIDList) > 0:
                            self.skinUsedBoneIDList.append(mat.skinUsedBoneIDList)
                #return self.matList
class rGeometryList(object):
        def __init__(self,datas,geometryCount,vertMatList):
                self.bs = NoeBitStream(datas)            
                self.geometryCount = geometryCount
                self.vertMatList = vertMatList
                self.matList =[]
        def readGeometry(self):
                
                for i in range(self.geometryCount):
                        vertMat = self.vertMatList[i]
                        geometryHeader = rwChunk(self.bs)
                        datas = self.bs.readBytes(geometryHeader.chunkSize)
                        geo = rGeomtry(datas,vertMat)
                        #print("GEO ID:",i)
                        geo.rGeometryStruct()
                        for m in range(len(geo.matList)):
                                self.matList.append(geo.matList[m])                             
class rSkin(object):
        def __init__(self,datas,numVert,nativeFlag):
                self.bs = NoeBitStream(datas)
                self.numVert = numVert
                self.nativeFlag = nativeFlag
                self.boneIndexs = bytes()
                self.boneWeights = bytes()
                self.usedBoneIndexList = []
        def readSkin(self):
                if self.nativeFlag != 1:
                        boneCount = self.bs.readByte()
                        usedBoneIDCount=self.bs.readByte()
                        maxNumWeights = self.bs.readByte()
                        unk2 = self.bs.readByte()
                        self.bs.seek(usedBoneIDCount,1)
                        self.boneIndexs = self.bs.readBytes(self.numVert*4)
                        self.boneWeights= self.bs.readBytes(self.numVert*16)
                        rapi.rpgBindBoneIndexBuffer(self.boneIndexs, noesis.RPGEODATA_UBYTE, 4 , 4)
                        rapi.rpgBindBoneWeightBuffer(self.boneWeights, noesis.RPGEODATA_FLOAT, 16, 4)
                        inverseBoneMats=[]
                        for i in range(boneCount):
                                inverseBoneMats.append(NoeMat44.fromBytes(self.bs.readBytes(64)))                        
                        self.bs.read('3f')

                else:
                        skinStruct = rwChunk(self.bs)
                        platform = self.bs.readUInt()
                        boneCount = self.bs.readUByte()
                        numUsedBone = self.bs.readUByte()
                        maxWeightsPerVertex = self.bs.readUByte()
                        padding = self.bs.readUByte()
                        self.usedBoneIndexList=[]
                        for i in range(numUsedBone):                            
                            self.usedBoneIndexList.append(self.bs.readUByte())      
                        inverseBoneMats=[]
                        for i in range(boneCount):
                                inverseBoneMats.append(NoeMat44.fromBytes(self.bs.readBytes(64)))
                        #self.bs.read('7i') #for ps2 dff
                        #self.bs.seek(16,1) #for Mortal Kombat PS2
class rBinMeshPLG(object):
        def __init__(self,datas,matList,nativeFlag):
                self.bs = NoeBitStream(datas)
                self.matList = matList
                self.nativeFlag = nativeFlag
                self.matIdList = []
                self.matIdNumFaceList = []
        def readFace(self):
                faceType = self.bs.readInt() # 1 = triangle strip
                numSplitMatID = self.bs.readUInt()
                indicesCount = self.bs.readUInt()
                for i in range(numSplitMatID):
                        faceIndices = self.bs.readUInt()
                        matID = self.bs.readUInt()
                        self.matIdList.append(matID)
                        self.matIdNumFaceList.append(faceIndices)
                        if self.nativeFlag != 1:
                                matName = self.matList[matID].name
                                rapi.rpgSetMaterial(matName)
                                tristrips = self.bs.readBytes(faceIndices*4)
                                rapi.rpgCommitTriangles(tristrips, noesis.RPGEODATA_UINT, faceIndices, noesis.RPGEO_TRIANGLE_STRIP, 1)
class materialTristripsInfo(object):
        def __init__(self,vertexCountStart,vertexCountEnd,tristripsCount,unknownCount):
                self.vertexCountStart = vertexCountStart
                self.vertexCountEnd = vertexCountEnd
                self.tristripsCount = tristripsCount
                self.unknownCount = unknownCount
class rMKPS2NativeDataPLG(object):
    def __init__(self,natvieDatas,matList,binMeshPLG,vertMat,skinUsedBoneIDList,skinFlag):
        self.bs = NoeBitStream(natvieDatas)
        self.matList = matList
        self.matIdList = binMeshPLG.matIdList
        self.matIdNumFaceList = binMeshPLG.matIdNumFaceList
        self.vertMat = vertMat  
        self.skinUsedBoneIDList = skinUsedBoneIDList
        self.skinFlag = skinFlag
    def readMesh(self):
        splitCount = len(self.matIdList)
        for i in range(splitCount):
            dataSize = self.bs.readUInt()
            meshType = self.bs.readUInt()
            endOfs = self.bs.tell() + dataSize
            vifEndOfs = endOfs
            vifSize = dataSize - 128
            checkPadEndFlag = 0
            while (checkPadEndFlag != 0x60):
                pad = self.bs.readUInt()
                checkPadEndFlag = (pad >> 24) & 0x60
                if checkPadEndFlag == 0x60:                        
                    vifSize = (pad & 0xffff) << 4
                    vifEndOfs = self.bs.tell() + 12 + vifSize   
                    self.bs.seek(12,NOESEEK_REL)
            vertDatas = []
            UVDatas =[]
            normalDatas = [] 
            colorDatas = []
            faceDatas = []    
            skinBoneIDs = []
            skinWeights = []
            realNumVertsList = []
            prevStripIDList = []
            vertIDList1Array = []
            vertIDList2Array = []
            sharedVertexIDList = []   
            MKPS2SkinDatas = []
            vifData =  self.bs.readBytes(vifSize)
            #print("VIFSIZE:",len(vifData))
            unpackData = rapi.unpackPS2VIF(vifData) 
            count0x71 = 4
            
            if self.skinFlag:
                usedBoneIDList = self.skinUsedBoneIDList[i]   
            else:
                count0x71 = 2
            vertStripIndex = -1
                        
            #Has UV SkinedModel , need reorder vertex list and copy new vertex to new list.
            #0x68 - vertex
            #0x6A - normal
            #0x65 - uv    
            #0x6E - 8bytes. vertex info section. byte4 = real numVert.
            #0x6D - Vertex shared list (the vertex ID of the previous strip to the next strip). The first triangle strip does not contain this data.
            #0x6D - if current strip missing some vertex id then will have this section.
            #0x71 chunk 1 = vertList 1 USHORT value; unkFlag = value & 0x2; vertID = value & 0x7FFC. skipFlag = value & 0x8000
            #0x71 chunk 4 = vertList 2
            #0x71 chunk 2 = skin chunk, UBYTE weight1/255; UBYTE boneID1; if weight1 and weight 2 == 0 , is only boneid1 used. weight = 1.0;
            #0x72 chunk 3 = skin chunk, UBYTE weight2/255; UBYTE boneID2;
            
            #No UV SkinedModel
            #0x68 Vertex float[3]
            #0x6A Normals byte[3]            
            #0x6E 4bytes. UBYTE1 boneid/4 - 1 ; UBYTE2 and UBYTE3 is zero; UBYTE4 skipFlag;
            
            #Has UV Non-SkinedModel
            #0x64 UV float[2]
            #0x68 Vertex float[3]
            #0x6A Normals byte[3]
            #0x6E Colors RGBA ubyte[4] 
            #0x71 chunk1 and chunk2 short;
            
           
            for up in unpackData:
                if up.numElems == 3 and up.elemBits == 32:
                        vertStripIndex += 1
                        #print("read vertex...",vertStripIndex,"numVert:",len(up.data)//12)
                        vertDatas.append(up.data)    
                       
                elif up.numElems == 2 and up.elemBits == 16:
                        UVDatas.append(getUV(up.data))
                elif up.numElems == 2 and up.elemBits == 32:  
                        UVDatas.append(up.data)
                elif up.numElems == 3 and up.elemBits == 8:
                        normals = getNormal(up.data)
                        normalDatas.append(normals)  
                elif up.numElems == 1 and up.elemBits == 16:
                        if self.skinFlag:
                            if count0x71 % 4 == 0:
                                vertIDList1 = getVertexIDList(up.data)
                                vertIDList1Array.append(vertIDList1)
                            if count0x71 % 4 == 3:
                                vertIDList2 = getVertexIDList(up.data)
                                vertIDList2Array.append(vertIDList2)
                            if count0x71 % 4 == 1:
                                MKPS2SkinDatas.append(up.data)
                            if count0x71 % 4 == 2:
                                MKPS2SkinDatas.append(up.data)                                
                        else:
                            if count0x71 % 2 == 0:
                                vertIDList1 = getVertexIDList2(up.data)
                                vertIDList1Array.append(vertIDList1)
                            if count0x71 % 2 == 1:
                                vertIDList2 = getVertexIDList2(up.data)
                                vertIDList2Array.append(vertIDList2)
                        count0x71 += 1                        
                elif up.numElems == 4 and up.elemBits == 8:  
                        if self.skinFlag:
                            if len(up.data) > 8: #skip has uv skined model header data
                                faceAndSkinData = createTriList6E(up.data,usedBoneIDList)
                                faceDatas.append(faceAndSkinData[0])
                                skinBoneIDs.append(faceAndSkinData[1])
                                skinWeights.append(faceAndSkinData[2])  
                            else:
                                realNumVertsList.append(noeUnpack("B",up.data[3:4])[0])
                        elif len(up.data) > 4 :
                            colorDatas.append(up.data)
                        elif len(up.data) == 4:
                            realNumVertsList.append(noeUnpack("B",up.data[3:4])[0])
                elif up.numElems == 4 and up.elemBits == 16:  
                        if self.skinFlag:
                            sharedIDList = getsharedVertexIDList(up.data)
                            sharedVertexIDList.append([(vertStripIndex+1),sharedIDList])
                        else:
                            sharedIDList = getsharedVertexIDList2(up.data)
                            sharedVertexIDList.append([(vertStripIndex+1),sharedIDList])
            paddingLength = endOfs - self.bs.tell()
            self.bs.seek(paddingLength,NOESEEK_REL)   
            newVertDatas = []
            newUVDatas = []
            newNormalDatas = []
            newColorDatas = []
            newSkipListDatas = []
            newSkinBoneIDs = []
            newSkinWeights = []
            #if len(vertIDList1Array) and self.skinFlag:
            #    mkps2SkinData = getMKPS2Skin(MKPS2SkinDatas,usedBoneIDList)
            #    skinBoneIDs = mkps2SkinData[0]
            #    skinWeights = mkps2SkinData[1]                
            numVertBlock = len(vertDatas)
            totalVertCount = 0   
            for v in range(numVertBlock):   
                tempFaceDatas = []
                #rapi.rpgSetName("mesh"+str(i) + "_" + str(v))
                vertBuffer = vertDatas[v]
                numVert = len(vertBuffer) // 12 
                normalData = normalDatas[v]   
                if len(UVDatas):
                    UVData = UVDatas[v]
                if len(colorDatas):
                    colorData = colorDatas[v]
                if len(skinBoneIDs):
                    boneIDs = skinBoneIDs[v]
                    weights = skinWeights[v]               
                if len(vertIDList1Array) and numVert > 2 and self.skinFlag:
                    
                
                    vertCount = realNumVertsList[v]
                    if not self.skinFlag:
                        maxVertID = 0
                        if maxVertID < vertIDList1Array[v][3]:
                            maxVertID =  vertIDList1Array[v][3]
                        if maxVertID < vertIDList2Array[v][3]:
                            maxVertID =  vertIDList2Array[v][3]                        
                        if v > 0:
                            for j in range(len(sharedVertexIDList)):                            
                                    if sharedVertexIDList[j][0] == v:
                                        for s in range(len(sharedVertexIDList[j][1][0])):                                            
                                            curStripVertID = sharedVertexIDList[j][1][1][s]        
                                            if maxVertID < curStripVertID:
                                                maxVertID = curStripVertID
                        vertCount = maxVertID + 1
                    #print("vertCount:",vertCount)
                    totalVertCount += vertCount
                    padVec3 = NoeVec3.fromBytes(vertBuffer[0:12])
                    padNomral = NoeVec3.fromBytes(normalData[0:12])                    
                    padUV = noeUnpack('2f',UVData[0:8])

                    vertList = [padVec3] * vertCount
                    normalList = [padNomral] * vertCount
                    uvList = [padUV] * vertCount
                    colorList = [[0,0,0,0]] * vertCount
                    boneIDList = [[0,0]] * vertCount
                    weightList = [[0.0,0.0]]* vertCount
                    
                    if len(skinBoneIDs):
                        padBoneID = noeUnpack('2B',boneIDs[0:2])
                        padWeight = noeUnpack('2f',weights[0:8])    
                        boneIDList = [padBoneID] * vertCount
                        weightList = [padWeight]* vertCount
                    if len(colorDatas):
                        padColor = noeUnpack('4B',colorData[0:4])
                        colorList = [padColor] * vertCount
                    skipList = [True] * vertCount
                    vertIDList = [False] * vertCount
                    vertIDList2 = ["missing"] * vertCount
                    for j in range(len(vertIDList1Array[v][0])):
                        vertID = vertIDList1Array[v][0][j]
                        vertList[vertID] = NoeVec3.fromBytes(vertBuffer[j*12:j*12+12])
                        normalList[vertID] = NoeVec3.fromBytes(normalData[j*12:j*12+12])
                        uvList[vertID] = noeUnpack('2f',UVData[j*8:j*8+8])
                        skipList[vertID] = vertIDList1Array[v][2][j]
                        vertIDList[vertID] = True
                        vertIDList2[vertID] = 1
                        if len(skinBoneIDs):
                            boneIDList[vertID] = noeUnpack('2B',boneIDs[j*2:j*2+2])
                            weightList[vertID] = noeUnpack('2f',weights[j*8:j*8+8])
                        if len(colorDatas):
                            colorList[vertID] = noeUnpack('4B',colorData[j*4:j*4+4])
                    for j in range(len(vertIDList2Array[v][0])):
                        vertID = vertIDList2Array[v][0][j]
                        #print(vertID,len(vertBuffer)//12)
                        vertList[vertID] = NoeVec3.fromBytes(vertBuffer[j*12:j*12+12])
                        normalList[vertID] = NoeVec3.fromBytes(normalData[j*12:j*12+12])
                        uvList[vertID] = noeUnpack('2f',UVData[j*8:j*8+8])
                        skipList[vertID] = vertIDList2Array[v][2][j]
                        vertIDList[vertID] = True
                        vertIDList2[vertID] = 1
                        if len(colorDatas):
                            colorList[vertID] = noeUnpack('4B',colorData[j*4:j*4+4])  
                        if len(skinBoneIDs):
                            boneIDList[vertID] = noeUnpack('2B',boneIDs[j*2:j*2+2])
                            weightList[vertID] = noeUnpack('2f',weights[j*8:j*8+8])                            
                    #print("mesh" + str(i) + "_" + str(v))
                    #print(vertIDList2)
                    #print("ori:",(len(vertBuffer) // 12 ),"new:",vertCount)
                    if v > 0:
                        for j in range(len(sharedVertexIDList)):                            
                                if sharedVertexIDList[j][0] == v:
                                    #print(sharedVertexIDList[j][1][0])
                                    #print(sharedVertexIDList[j][1][1])
                                    for s in range(len(sharedVertexIDList[j][1][0])):
                                        prevStripVertID = sharedVertexIDList[j][1][0][s]
                                        curStripVertID = sharedVertexIDList[j][1][1][s]
                                        vid = prevStripVertID                                    
                                        prevStripID = v - 1
                                        #print(curStripVertID,vid)
                                        vertList[curStripVertID] = NoeVec3.fromBytes(newVertDatas[prevStripID][vid*12:vid*12+12])
                                        normalList[curStripVertID] = NoeVec3.fromBytes(newNormalDatas[prevStripID][vid*12:vid*12+12])
                                        uvList[curStripVertID] = noeUnpack('2f',newUVDatas[prevStripID][vid*8:vid*8+8])
                                        skipList[curStripVertID] = sharedVertexIDList[j][1][2][s]                                                                         
                                        if len(skinBoneIDs):
                                            boneIDList[curStripVertID] = noeUnpack('2B', newSkinBoneIDs[prevStripID][vid*2:vid*2+2])
                                            weightList[curStripVertID] = noeUnpack('2f',newSkinWeights[prevStripID][vid*8:vid*8+8])
                                        vertIDList2[curStripVertID] = "prev" + str(vid) 
                    #print(vertIDList2)
                    newVertBuffer = bytes()
                    newNormalBuffer = bytes()
                    newUVBuffer = bytes()
                    newColorBuffer = bytes()
                    newBoneIDBuffer = bytes()
                    newWeightBuffer = bytes()
                    for j in range(vertCount):
                        vert = vertList[j]
                        newVertBuffer += vert.toBytes()
                        normal = normalList[j]
                        newNormalBuffer += normal.toBytes()
                        uv = uvList[j]
                        newUVBuffer += noePack('2f',uv[0],uv[1])
                        if len(colorDatas):   
                            color = colorList[j]
                            newColorBuffer += noePack('4B',color[0],color[1],color[2],color[3])
                        if len(skinBoneIDs):
                            tempBoneIDs = boneIDList[j]
                            tempWeights = weightList[j]
                            newBoneIDBuffer += noePack('2B',tempBoneIDs[0],tempBoneIDs[1])
                            newWeightBuffer += noePack('2f',tempWeights[0],tempWeights[1])                            
                    vertBuffer = newVertBuffer
                    newVertDatas.append(newVertBuffer)
                    normalData = newNormalBuffer
                    newNormalDatas.append(newNormalBuffer)
                    UVData = newUVBuffer
                    newUVDatas.append(newUVBuffer)
                    newSkipListDatas.append(skipList)
                    faceBuffer = createTriList(skipList)                    
                    tempFaceDatas.append(faceBuffer)
                    if len(colorDatas): 
                        colorData = newColorBuffer
                        newColorDatas.append(newColorBuffer)
                    if len(skinBoneIDs):
                        boneIDs = newBoneIDBuffer
                        weights = newWeightBuffer
                        newSkinBoneIDs.append(newBoneIDBuffer)
                        newSkinWeights.append(newWeightBuffer)

                    
                vertBuffer = getTransformVertex(vertBuffer,self.vertMat)       
                rapi.rpgBindPositionBuffer(vertBuffer, noesis.RPGEODATA_FLOAT, 12) 
                numVert = len(vertBuffer) // 12 
                #print("numVert:",numVert)               
                normalData = getTransformNormal(normalData,self.vertMat)
                rapi.rpgBindNormalBuffer(normalData, noesis.RPGEODATA_FLOAT, 12)
                if len(UVDatas):
                    rapi.rpgBindUV1Buffer(UVData, noesis.RPGEODATA_FLOAT, 8)                      
                if len(colorDatas):              
                        rapi.rpgBindColorBuffer(colorData, noesis.RPGEODATA_UBYTE, 4, 4)                   
                matID = self.matIdList[i]
                matName = self.matList[matID].name
                #matName = "mtl" + str(i) + "_" + str(v)
                rapi.rpgSetMaterial(matName)
                
                if len(skinBoneIDs):
                    if len(skinBoneIDs[v]) // numVert == 4:          #for no uv skined model                     
                        rapi.rpgBindBoneIndexBuffer(skinBoneIDs[v], noesis.RPGEODATA_INT, 4, 1)
                        rapi.rpgBindBoneWeightBuffer(skinWeights[v], noesis.RPGEODATA_FLOAT, 4, 1)  
                    #else:                                            #for has uv skined model
                    #    rapi.rpgBindBoneIndexBuffer(boneIDs, noesis.RPGEODATA_UBYTE, 2, 2)
                    #    rapi.rpgBindBoneWeightBuffer(weights, noesis.RPGEODATA_FLOAT, 8, 2) 
                if len(faceDatas):
                    if numVert > 2 : 
                        faceBuffer = faceDatas[v] 
                        rapi.rpgCommitTriangles(faceBuffer, noesis.RPGEODATA_INT, len(faceBuffer)//4, noesis.RPGEO_TRIANGLE, 1)  
                elif len(tempFaceDatas) > 0:
                        faceBuffer = tempFaceDatas[0] 
                        rapi.rpgCommitTriangles(faceBuffer, noesis.RPGEODATA_INT, len(faceBuffer)//4, noesis.RPGEO_TRIANGLE, 1)
                elif numVert > 2:                  
                    rapi.rpgCommitTriangles(None, noesis.RPGEODATA_INT, len(vertBuffer)//12, noesis.RPGEO_TRIANGLE_STRIP, 1)
                
                rapi.rpgClearBufferBinds()
            #print(i,"totalVertCount:",totalVertCount)
def getMKPS2Skin(flagData,usedBoneIDList):      
    numBlock = len(flagData) // 2
    boneIDsList = []
    weightsList = []
    for i in range(numBlock):
        bin1 = NoeBitStream(flagData[i*2])
        bin2 = NoeBitStream(flagData[i*2+1])
        boneIDs = bytes()
        weights = bytes()
        numVert = len(flagData[i*2]) // 2
        for j in range(numVert):
            weight1 = bin1.readUByte()
            boneID1 = bin1.readUByte() // 4
            weight2 = bin2.readUByte()
            boneID2 = bin2.readUByte() // 4
            if weight1 == 0:
                #print(1,boneID1,boneID2)
                #print(1,usedBoneIDList)
                boneIDs += noePack('2B',usedBoneIDList[boneID2-1],0)
                weights += noePack('2f',1.0,0)
            else:
                #print(2,boneID1,boneID2)
                #print(2,usedBoneIDList)            
                w1 = weight1 / 255.0
                w2 = (255 - weight1) / 255.0
                b1 = usedBoneIDList[boneID1-1]
                b2 = usedBoneIDList[boneID2-1]
                boneIDs += noePack('2B',b1,b2)
                weights += noePack('2f',w1,w2)
        boneIDsList.append(boneIDs)
        weightsList.append(weights)
    return [boneIDsList,weightsList]
            
        
        
def getsharedVertexIDList(flagData):  
    vin = NoeBitStream(flagData)
    numVerts = len(flagData) // 2
    prevStripVertexIDList = []
    curStripVertexIDList = []
    skipList1 = []
    skipList2 = []
    for i in range (numVerts):     
        value = vin.readUShort()
        unkFlag = value & 0x2
        skipFlag = (value & 0x8000) == 0x8000  
        if unkFlag == 2:
            vertID = ((value & 0x7FFC) - 128) // 4
        elif unkFlag == 0:
            vertID = (value & 0x7FFC) // 4 - 122
        if i % 2 == 0:
            prevStripVertexIDList.append(vertID)
            skipList1.append(skipFlag)
        elif i % 2 == 1:
            curStripVertexIDList.append(vertID)
            skipList2.append(skipFlag)
    return [prevStripVertexIDList,curStripVertexIDList,skipList1,skipList2]
def getsharedVertexIDList2(flagData):  
    vin = NoeBitStream(flagData)
    numVerts = len(flagData) // 2
    prevStripVertexIDList = []
    curStripVertexIDList = []
    skipList1 = []
    skipList2 = []
    dataType = False
    dataType2 = False
    for i in range (numVerts):    
        value = vin.readUShort()
        unkFlag = value & 0x3
        vertID = (value & 0x7FFC) // 4
        if vertID >= 180:
            vertID -= 180
        else:
            vertID -= 59        
        skipFlag = (value & 0x8000) == 0x8000  
        if i % 2 == 0:       
            prevStripVertexIDList.append(vertID)
            skipList1.append(skipFlag)
        elif i % 2 == 1:
            curStripVertexIDList.append(vertID)
            skipList2.append(skipFlag)
    return [prevStripVertexIDList,curStripVertexIDList,skipList1,skipList2]    
def getVertexIDList(flagData):
    vin = NoeBitStream(flagData)
    numVerts = len(flagData) // 2  
    vertIDList = []
    unkFlagList = []
    skipFlagList = []
    for i in range (numVerts): 
        value = vin.readUShort()
        unkFlag = value & 0x2
        if unkFlag == 2:
            vertID = ((value & 0x7FFC) - 128) // 4
        elif unkFlag == 0:
            vertID = (value & 0x7FFC) // 4 - 122
        skipFlag = (value & 0x8000) == 0x8000             
        if (value & 0x7FFC) >= 0:
            vertIDList.append(vertID)
            unkFlagList.append(unkFlag)
            skipFlagList.append(skipFlag)
    return [vertIDList,unkFlagList,skipFlagList]
def getVertexIDList2(flagData):
    vin = NoeBitStream(flagData)
    numVerts = len(flagData) // 2  
    vertIDList = []
    unkFlagList = []
    skipFlagList = []
    dataType = False
    maxVertID = 0 
    for i in range (numVerts): 
        value = vin.readUShort()
        unkFlag = value & 0x3
        vertID = (value & 0x7FFC) // 4
        if vertID >= 180:
            vertID -= 180
        else:
            vertID -= 59          
        skipFlag = (value & 0x8000) == 0x8000              
        vertIDList.append(vertID)
        unkFlagList.append(unkFlag)
        skipFlagList.append(skipFlag)
        if maxVertID < vertID:
            maxVertID = vertID
    return [vertIDList,unkFlagList,skipFlagList,maxVertID]    
def createTriList(skipList):
    out = NoeBitStream()
    numVerts = len(skipList)
    startDir = -1
    faceDir = startDir
    f1 = 0
    f2 = 1
    for i in range (numVerts):        
        f3 = i
        skipFlag = skipList[i] #skip Isolated vertex      
        faceDir *= -1   
        if skipFlag != True:
            if f1 != f2 and f2 != f3 and f3 != f1:
                if faceDir > 0:
                    out.writeInt(f1)
                    out.writeInt(f2)
                    out.writeInt(f3)
                else:
                    out.writeInt(f2)
                    out.writeInt(f1)
                    out.writeInt(f3)            
                #print(f1,f2,f3)
        f1 = f2
        f2 = f3         
    return out.getBuffer()  
def createTriList6E(flagData,usedBoneIDList):
    vin = NoeBitStream(flagData)
    out = NoeBitStream()
    numVerts = len(flagData)//4
    faceDir = 1
    f1 = 0
    f2 = 1
    boneIDs = bytes()
    weights = bytes()  
    #print("start")
    for i in range (numVerts):   
        boneID1 = vin.readUByte() // 4 #always only use boneID1
        weight1 = vin.readUByte() #always 0
        boneID2 = vin.readUByte() #always 0
        bitFlag = vin.readUByte() #weight2 always 0
        weight2 = bitFlag & 0xFE
        #print(boneID1,weight1,boneID2,weight2)
        weights += noePack("f",1.0)
        boneIDs += noePack("i",usedBoneIDList[boneID1-1])
        f3 = i
        skipFlag = bitFlag & 0x1 #skip Isolated vertex
        if skipFlag != 1:
            if f1 != f2 and f2 != f3 and f3 != f1:
                if faceDir > 0:
                    out.writeInt(f1)
                    out.writeInt(f2)
                    out.writeInt(f3)
                else:
                    out.writeInt(f2)
                    out.writeInt(f1)
                    out.writeInt(f3)
        faceDir *= -1
        f1 = f2
        f2 = f3
    #print("end")
    return [out.getBuffer(),boneIDs,weights]    
class rNativeDataPLG(object):
        def __init__(self,datas,matList,binMeshPLG,vertMat):
                self.bs = NoeBitStream(datas)
                self.matList = matList
                self.matIdList = binMeshPLG.matIdList
                self.matIdNumFaceList = binMeshPLG.matIdNumFaceList
                self.vertMat = vertMat
        def readMesh(self):
                natvieStruct = rwChunk(self.bs)
                platform = self.bs.readUInt()
                splitCount = len(self.matIdList)
                for i in range(splitCount):
                    dataSize = self.bs.readUInt()
                    meshType = self.bs.readUInt()
                    endOfs = self.bs.tell() + dataSize
                    #vifEndOfs = endOfs
                    vifSize = dataSize
                    if meshType == 0:
                        strowCode = self.bs.readUInt()
                        VIFn_R0 = self.bs.readUInt()
                        VIFn_R1 = self.bs.readUInt()
                        VIFn_R2 = self.bs.readUInt()
                        VIFn_R3 = self.bs.readUInt()
                        #vifEndOfs = bs.tell() - 20 + VIFn_R0 * 16
                        vifSize = VIFn_R0 * 16
                        self.bs.seek(-20,NOESEEK_REL)
                    vertDatas = []
                    faceDatas = []
                    UVDatas =[]
                    normalDatas = []
                    skinBoneIDs = []
                    skinWeights = []
                    colorDatas = []            
                    vifData =  self.bs.readBytes(vifSize)
                    unpackData = rapi.unpackPS2VIF(vifData)                    
                    for up in unpackData:
                        if up.numElems == 3 and up.elemBits == 32:
                                vertDatas.append(up.data)    
                                faceDatas.append(getTriangleList(up.data))
                        elif up.numElems == 2 and up.elemBits == 32:
                                UVDatas.append(up.data)
                        elif up.numElems == 4 and up.elemBits == 8:
                                colorDatas.append(up.data) 
                        elif up.numElems == 3 and up.elemBits == 8:
                                normals = getNormal(up.data)
                                normalDatas.append(normals)                               
                    if meshType == 0:
                        for j in range(self.matIdNumFaceList[i]):
                            temp = bytearray(16)
                            for t in range(16):
                                temp[t] = self.bs.readUByte()                            
                            boneID1 = noeUnpack('B',temp[0:1])[0] // 4
                            boneID2 = noeUnpack('B',temp[4:5])[0] // 4
                            boneID3 = noeUnpack('B',temp[8:9])[0] // 4
                            boneID4 = noeUnpack('B',temp[12:13])[0] // 4                            
                            temp[0] = 0
                            temp[4] = 0
                            temp[8] = 0
                            temp[12] = 0                                   
                            weight1,weight2,weight3,weight4 = noeUnpack('4f',temp)
                            if weight1 > 0:
                                boneID1 -= 1
                            if weight2 > 0:
                                boneID2 -= 1
                            if weight3 > 0:
                                boneID3 -= 1
                            if weight4 > 0:
                                boneID4 -= 1                                
                            skinBoneIDs.append((boneID1,boneID2,boneID3,boneID4))
                            skinWeights.append((weight1,weight2,weight3,weight4))
                    paddingLength = endOfs - self.bs.tell()
                    self.bs.seek(paddingLength,NOESEEK_REL)
                    
                    #For triangle strips the last two vertices of the last triangle are used as the first two of the next one. 
                    #Similarly for line strips the last vertex of the last line segment is used as the first vertex for the next one. 
                    #In triangle and line lists every vertex is only used once.
                    numVertBlock = len(vertDatas)
                    skinDataIndex = 0
                    newSkinBoneIDs = []
                    newSkinWeights = []  
                    if meshType == 0:                  
                        for v in range(numVertBlock):           
                            stripNumVert = len(vertDatas[v])//12
                            boneIDs = bytes()
                            weights = bytes()
                            if v > 0:  
                                stripNumVert -= 2
                                w = 2
                                for j in range(w):
                                    boneID = skinBoneIDs[skinDataIndex-(w-j)]
                                    weight = skinWeights[skinDataIndex-(w-j)]
                                    boneIDs += noePack('4B',boneID[0],boneID[1],boneID[2],boneID[3])
                                    weights += noePack('4f',weight[0],weight[1],weight[2],weight[3])                            
                            for j in range(stripNumVert):                            
                                boneID = skinBoneIDs[skinDataIndex+j]
                                weight = skinWeights[skinDataIndex+j]
                                boneIDs += noePack('4B',boneID[0],boneID[1],boneID[2],boneID[3])
                                weights += noePack('4f',weight[0],weight[1],weight[2],weight[3])
                            skinDataIndex += stripNumVert                        
                            newSkinBoneIDs.append(boneIDs)
                            newSkinWeights.append(weights)    
                    #rapi.rpgSetName()                                
                    numVertBlock = len(vertDatas)
                    for v in range(numVertBlock):                        
                        vertBuffer = vertDatas[v]                        
                        vertBuffer = getTransformVertex(vertBuffer,self.vertMat)                  
                        rapi.rpgBindPositionBuffer(vertBuffer, noesis.RPGEODATA_FLOAT, 12)
                        
                        if meshType == 0:                            
                            rapi.rpgBindBoneIndexBuffer(newSkinBoneIDs[v], noesis.RPGEODATA_UBYTE, 4, 1)
                            rapi.rpgBindBoneWeightBuffer(newSkinWeights[v], noesis.RPGEODATA_FLOAT, 4, 1)       
                            
                        normalData = normalDatas[v]                        
                        normalData = getTransformNormal(normalData,self.vertMat)
                        rapi.rpgBindNormalBuffer(normalData, noesis.RPGEODATA_FLOAT, 12)

                        UVData = UVDatas[v]
                        checkLODUV = noeUnpack("I",UVData[0:4])[0]                    
                        if checkLODUV != 0xE5E5E5E5:
                            rapi.rpgBindUV1Buffer(UVData, noesis.RPGEODATA_FLOAT, 8)                    

                        colorData = colorDatas[v]                
                        rapi.rpgBindColorBuffer(colorData, noesis.RPGEODATA_UBYTE, 4, 4)
                                             
                        matID = self.matIdList[i]
                        matName = self.matList[matID].name
                        rapi.rpgSetMaterial(matName)
                        if meshType == 0:
                            faceBuffer = faceDatas[v]
                            rapi.rpgCommitTriangles(faceBuffer, noesis.RPGEODATA_INT, len(faceBuffer)//4, noesis.RPGEO_TRIANGLE, 1)
                        else:
                            rapi.rpgCommitTriangles(None, noesis.RPGEODATA_INT, len(vertBuffer)//12, noesis.RPGEO_TRIANGLE_STRIP, 1)
                            
                        rapi.rpgClearBufferBinds()
def getTriangleList(vertBuffer):
    triangleList = []
    triangleDir = 1                        
    for j in range(len(vertBuffer)//12-2):
        v1 = noeUnpack('3f',vertBuffer[j*12:j*12+12])
        v2 = noeUnpack('3f',vertBuffer[(j+1)*12:(j+1)*12+12])
        v3 = noeUnpack('3f',vertBuffer[(j+2)*12:(j+2)*12+12])
        f1 = j
        f2 = j + 1
        f3 = j + 2
        if v1 != v2 and v2 != v3 and v1 != v3:
            if triangleDir > 0:
                triangleList.append((f1,f2,f3))
            else:
                triangleList.append((f2,f1,f3))
        triangleDir *= -1
    faceBuffer = bytes()
    for j in range(len(triangleList)):
        faceBuffer += noePack('3I',triangleList[j][0],triangleList[j][1],triangleList[j][2])    
    return faceBuffer
def getTransformVertex(vertBuffer,parentBoneMatrix):
    vin = NoeBitStream(vertBuffer)
    out = NoeBitStream()
    numVerts = len(vertBuffer) // 12
    for i in range(numVerts):
        vert = NoeVec3.fromBytes(vin.readBytes(12))
        vert *= parentBoneMatrix        
        out.writeBytes(vert.toBytes())
    return out.getBuffer()
def getUV(uvdata):
    uvin = NoeBitStream(uvdata)
    out = NoeBitStream()
    numVerts = len(uvdata) // 4
    for i in range(numVerts):
        u = uvin.readShort() / 4096.0
        v = uvin.readShort() / 4096.0
        out.writeFloat(u)
        out.writeFloat(v)
    return out.getBuffer()  
def getTransformNormal(normalData,parentBoneMatrix):
    nin = NoeBitStream(normalData)
    out = NoeBitStream()
    numVerts = len(normalData) // 12
    for i in range(numVerts):
        normal = NoeVec3.fromBytes(nin.readBytes(12))
        normal *= parentBoneMatrix
        normal.normalize()
        out.writeBytes(normal.toBytes())
    return out.getBuffer()
    
def getNormal(normalData):
    nin = NoeBitStream(normalData)
    out = NoeBitStream()
    numVerts = len(normalData) // 3
    for i in range(numVerts):
        nx = nin.readByte() / 128.0
        ny = nin.readByte() / 128.0
        nz = nin.readByte() / 128.0
        out.writeFloat(nx)
        out.writeFloat(ny)
        out.writeFloat(nz)        
    return out.getBuffer()
class rGeomtry(object):
        def __init__(self,datas,vertMat):
                self.bs = NoeBitStream(datas)
                self.vertMat = vertMat
                self.matList = []
        def rGeometryStruct(self):
                geoStruct = rwChunk(self.bs)
                FormatFlags = self.bs.readUShort()
                numUV = self.bs.readByte()
                nativeFlags = self.bs.readByte()
                numFace = self.bs.readUInt()
                numVert = self.bs.readUInt()
                numMorphTargets = self.bs.readUInt()
                Tristrip = FormatFlags % 2
                Meshes = (FormatFlags & 3) >> 1
                Textured = (FormatFlags & 7) >> 2
                Prelit = (FormatFlags & 0xF) >> 3
                Normals = (FormatFlags & 0x1F) >> 4
                Light = (FormatFlags & 0x3F) >> 5
                ModulateMaterialColor = (FormatFlags & 0x7F) >> 6
                Textured_2 = (FormatFlags & 0xFF) >> 7;
                MKPS2SkinFlag = (FormatFlags & 0x100) == 0x100
                MtlIDList = []
                faceBuff = bytes()
                vertBuff = bytes()
                normBuff = bytes()
                uvs = None
                if nativeFlags != 1:
                        if (Prelit==1):
                                self.bs.seek(numVert*4,1)
                        if (Textured == 1):
                                uvs = self.bs.readBytes(numVert * 8)
                                rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
                        if (Textured_2==1):
                                uvs = self.bs.readBytes(numVert * 8)              
                                self.bs.seek(numVert*8,1)
                                rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
                        if (Meshes==1):                        
                                for i in range(numFace):
                                        f2 = self.bs.readBytes(2)
                                        f1 = self.bs.readBytes(2)
                                        MtlIDList.append(self.bs.readUShort())
                                        f3 = self.bs.readBytes(2)
                                        faceBuff+=f1
                                        faceBuff+=f2
                                        faceBuff+=f3                                
                sphereXYZ = NoeVec3.fromBytes(self.bs.readBytes(12))
                sphereRadius = self.bs.readFloat()
                positionFlag = self.bs.readUInt()
                normalFlag = self.bs.readUInt()
                if nativeFlags != 1:
                        if (Meshes==1):
                                #vertBuff = self.bs.readBytes(numVert * 12)
                                for i in range(numVert):
                                        vert = NoeVec3.fromBytes(self.bs.readBytes(12))
                                        vert *= self.vertMat
                                        vertBuff+=vert.toBytes()
                                        rapi.rpgBindPositionBuffer(vertBuff, noesis.RPGEODATA_FLOAT, 12)
                        if (Normals==1):
                                #normBuff = self.bs.readBytes(numVert * 12)
                                for i in range(numVert):
                                        normal = NoeVec3.fromBytes(self.bs.readBytes(12))
                                        normal *= self.vertMat
                                        normBuff+=normal.toBytes()        
                                        rapi.rpgBindNormalBuffer(normBuff, noesis.RPGEODATA_FLOAT, 12)
                matrialListHeader = rwChunk(self.bs)
                matDatas = self.bs.readBytes(matrialListHeader.chunkSize)
                rMatList = rMaterialList(matDatas)
                rMatList.getMaterial()
                matList = rMatList.matList
                texList = rMatList.texList
                for m in range(len(matList)):
                        self.matList.append(matList[m])
                geoExtHeader = rwChunk(self.bs)
                geoExtEndOfs = self.bs.tell()+geoExtHeader.chunkSize

                haveSkin = 0
                haveBinMesh = 0
                haveNavtiveMesh = 0
                while self.bs.tell()<geoExtEndOfs:
                        header = rwChunk(self.bs)
                        if header.chunkID == 0x50e:
                                haveBinMesh = 1
                                binMeshDatas = self.bs.readBytes(header.chunkSize)                    
                        elif header.chunkID == 0x116:
                                haveSkin = 1
                                skinDatas = self.bs.readBytes(header.chunkSize)
                        elif header.chunkID == 0x510:
                                haveNavtiveMesh = 1
                                nativeDatas = self.bs.readBytes(header.chunkSize)                                
                        else:
                             self.bs.seek(header.chunkSize,1)
                if haveSkin:
                        skin = rSkin(skinDatas,numVert,nativeFlags)
                        skin.readSkin()
                if haveBinMesh:
                        binMeshPLG = rBinMeshPLG(binMeshDatas,matList,nativeFlags)
                        binMeshPLG.readFace()
                if haveNavtiveMesh:
                        nativeDataPLG = rNativeDataPLG(nativeDatas,matList,binMeshPLG,self.vertMat)
                        nativeDataPLG.readMesh()
                if nativeFlags == 1 and geoStruct.chunkSize > 40:   
                #if isMKPS2:
                        splitCount = len(binMeshPLG.matIdList)
                        start = self.bs.tell()
                        nativeChunkSize = 0
                        for i in range(splitCount):
                            dataSize = self.bs.readUInt()
                            meshType = self.bs.readUInt()
                            endOfs = self.bs.tell() + dataSize
                            self.bs.seek(endOfs)
                            nativeChunkSize += (dataSize + 8)
                        self.bs.seek(start)                        
                        natvieDatas = self.bs.readBytes(nativeChunkSize)                            
                        if MKPS2SkinFlag:
                            skinDataSize = geoStruct.chunkSize - 40 - nativeChunkSize
                            skinDatas = self.bs.readBytes(skinDataSize)
                            skin = rSkin(skinDatas,numVert,nativeFlags)
                            skin.readSkin()
                        MKPS2NativeDataPLG = rMKPS2NativeDataPLG(natvieDatas,matList,binMeshPLG,self.vertMat,rMatList.skinUsedBoneIDList,MKPS2SkinFlag)
                        MKPS2NativeDataPLG.readMesh()
                #rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, (numFace * 3), noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()
