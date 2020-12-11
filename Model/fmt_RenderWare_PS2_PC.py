#RenderWare DFF Models and TXD Textures Noesis Importer
#RenderWare Version 3.7.0.2 (0x1C020065)
#By Allen(Leeao)
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
    if idstring not in (0x10,0x24):
            return 0
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
def dffLoadModel(data, mdlList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()        
    fileSize = len(data)
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
                self.hasAnim = 0
                self.kickDummy = 0
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
                        self.hasAnim = 1
                        flags = self.bs.readInt()
                        keyFrameSize = self.bs.readInt()
                        for i in range(boneCount):
                                self.hAnimBoneIDList.append(self.bs.readInt())
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
        def rFrameExt(self,index):
                header = rwChunk(self.bs)
                endOfs = self.bs.tell() + header.chunkSize
                hasName = 0
                if header.chunkSize:
                        while (self.bs.tell()<endOfs):
                                chunk = rwChunk(self.bs)                                
                                if chunk.chunkID == 0x11e:
                                        self.rHAnimPLG()
                                elif chunk.chunkID == 0x11f:
                                        hasName = 1
                                        self.rUserDataPLG(index)
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
                #Sort by skin bone ID, starting from 0.
                newAnimBoneIDList = self.hAnimBoneIDList
                newParentBoneIDList = [0] * (self.frameCount - 1)
                newBoneNameList = [0] * (self.frameCount - 1)
                newBoneMatrixList = [0] * (self.frameCount - 1)
                if len(self.hAnimBoneIDList) > 0:
                    for i in range(len(self.hAnimBoneIDList)):
                        animBoneID = newAnimBoneIDList[i]                        
                        if animBoneID in self.animBoneIDList:
                            #because rootbone at frameList id start is 1 (not include first dummy(0)) . 0 is dummy not use.
                            srcBoneArrayIndex = self.animBoneIDList.index(animBoneID) + 1 
                            srcBoneParentListID = self.bonePrtIdList[srcBoneArrayIndex]
                            if srcBoneParentListID == 0:
                                newParentBoneIDList[i] = -1
                            else:
                                #because rootBone animBoneID not include first dummy(0),so convert to frameList ID need - 1.                            
                                srcParentAnimBoneID = self.animBoneIDList[srcBoneParentListID-1] 
                                if srcParentAnimBoneID in newAnimBoneIDList:
                                    arrayIndex = newAnimBoneIDList.index(srcParentAnimBoneID)      
                                    newParentBoneIDList[i] = arrayIndex                    
                    for i in range(len(self.hAnimBoneIDList)):
                        animBoneID = newAnimBoneIDList[i]
                        if animBoneID in self.animBoneIDList:
                            #because rootbone at frameList id start is 1 (not include first dummy(0)).so convert to frameList ID need + 1. 0 is dummy not use.
                            arrayIndex = self.animBoneIDList.index(animBoneID) + 1  
                            newBoneNameList[i] = "Bone" + str(animBoneID)
                            newBoneMatrixList[i] = self.boneMatList[arrayIndex]
                    bones=[]
                    for j in range(len(newAnimBoneIDList)):                
                            boneIndex = j
                            boneName =  newBoneNameList[j]
                            boneMat = newBoneMatrixList[j]
                            bonePIndex = newParentBoneIDList[j]
                            bone = NoeBone(boneIndex, boneName, boneMat, None,bonePIndex)
                            bones.append(bone)
                    for j in range(len(newAnimBoneIDList)):
                            bonePIndex = newParentBoneIDList[j]
                            if(bonePIndex>-1):
                                    prtMat=bones[bonePIndex].getMatrix()
                                    boneMat = bones[j].getMatrix()                             
                                    bones[j].setMatrix(boneMat * prtMat)
                            else:
                                    prtMat=self.bones[0].getMatrix()
                                    boneMat = bones[j].getMatrix()                             
                                    bones[j].setMatrix(boneMat * prtMat)                                    
                    self.skinBones = bones
                else:
                    bones = self.bones       
                return bones
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
        def rMaterialStruct(self):
                header = rwChunk(self.bs)
                unused = self.bs.readInt()
                rgba = self.bs.readInt()
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
                        alphaTexName = noeStrFromBytes(self.bs.readBytes(rwChunk(self.bs).chunkSize))
                        texExtHeader = rwChunk(self.bs)
                        self.bs.seek(texExtHeader.chunkSize,1)
                matExtHeader = rwChunk(self.bs)
                self.bs.seek(matExtHeader.chunkSize,1)
                return texName
                        
class rMaterialList(object):
        def __init__(self,datas):
                self.bs = NoeBitStream(datas)            
                self.matCount = 0
                self.matList = []
                self.texList = []
        def rMaterialListStruct(self):
                header = rwChunk(self.bs)
                self.matCount = self.bs.readUInt()
                self.bs.seek(self.matCount*4,1)
        def getMaterial(self):
                self.rMaterialListStruct()
                for i in range(self.matCount):
                        matData = self.bs.readBytes(rwChunk(self.bs).chunkSize)
                        texName = rMatrial(matData).rMaterialStruct()
                        self.texList.append(texName)
                        #matName = "material[%d]" %len(self.matList)
                        matName = texName
                        material = NoeMaterial(matName, texName)
                        material.setDefaultBlend(0)
                        self.matList.append(material)
                        #texture = NoeTexture()
                        self.texList.append(texName)                        
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
                        boneIndexList=[]
                        for i in range(numUsedBone):                            
                            boneIndexList.append(self.bs.readUByte())      
                        inverseBoneMats=[]
                        for i in range(boneCount):
                                inverseBoneMats.append(NoeMat44.fromBytes(self.bs.readBytes(64)))                        
                        self.bs.read('7i')
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
                #rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, (numFace * 3), noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()                

