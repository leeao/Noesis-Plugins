#by Allen
from inc_noesis import *
import struct
def registerNoesisTypes():
	handle = noesis.register("Evil Dead Regeneration PC pak model texture", ".pak")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, pakLoadModel)
	return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        bs.seek(0xc)
        idstring = noeStrFromBytes(bs.readBytes(4))
        if idstring != "XXXX":
                return 0
        return 1

def pakLoadModel(data, mdlList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()        
        ms = NoeBitStream()
        bs.seek(0x30)
        chunkEndOfs = 0x50
        for i in range(2):
                chunkName = noeStrFromBytes(bs.readBytes(4))
                chunkFlag = bs.readInt()
                chunkOffset = bs.readInt()
                chunkSize = bs.readInt()
                if chunkName =="2pr.":
                        chunkEndOfs += chunkSize
                        break
        texList = []
        bs.seek(0x50)
        while (bs.tell()<chunkEndOfs):
                chunk=rwChunk(bs)
                if chunk.chunkID == 0x16:
                        rtex = rTex(bs.readBytes(chunk.chunkSize))
                        rtex.rTexList()
                        texList = rtex.texList
                elif chunk.chunkID == 0x10:
                        clumpEndOfs = bs.tell()+chunk.chunkSize                      
                        clumpStructHeader = rClumpStruct(bs)
                        
                        framtListHeader = rwChunk(bs)
                        datas = bs.readBytes(framtListHeader.chunkSize)
                        frameList = rFrameList(datas)
                        bones = frameList.readBoneList()
                        skinBones = frameList.getSkinBones()
                        geometryListHeader = rwChunk(bs)
                        geometryListStructHeader = rwChunk(bs)
                        geometryCount = bs.readUInt()
                        if geometryCount:
                                datas = bs.readBytes(geometryListHeader.chunkSize-16)
                        vertMatList=[0]*clumpStructHeader.numAtomics
                        if clumpStructHeader.numAtomics:
                                atomicData = bytes()
                                for i in range(clumpStructHeader.numAtomics):
                                        atomicHeader = rwChunk(bs)
                                        atomicData += bs.readBytes(atomicHeader.chunkSize)
                                atomicList = rAtomicList(atomicData,clumpStructHeader.numAtomics).rAtomicStuct()
                                for j in range(clumpStructHeader.numAtomics):
                                        vertMatList[atomicList[j].geometryIndex]= bones[atomicList[j].frameIndex].getMatrix()
                        if geometryCount:
                                geometryList = rGeometryList(datas,geometryCount,vertMatList)
                                geometryList.readGeometry()                                
                                mdl = rapi.rpgConstructModel()
                                matList = []
                                for tex in texList:
                                        matName = tex.name
                                        material = NoeMaterial(matName, tex.name)
                                        material.setDefaultBlend(0)
                                        matList.append(material)
                                mdl.setModelMaterials(NoeModelMaterials(texList,matList))
                                mdl.setBones(skinBones)
                                mdlList.append(mdl)
                                rapi.rpgReset()
                                
                                
                        bs.seek(clumpEndOfs)
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
                if texFormatExt == 0x2000:
                        palette = self.bs.readBytes(1024) #256 colors
                elif texFormatExt == 0x4000:
                        palette = self.bs.readBytes(64) #16 colors
                        self.bs.seek(64,1)#skip padding
                pixelBuff = self.bs.readBytes(pixelBuffSize)

                if depth == 32:
                        if compressed == 1:
                                texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT1)
                        elif compressed == 0:
                                pixelBuff = rapi.imageFromMortonOrder(pixelBuff,width,height)
                                texData = rapi.imageDecodeRaw(pixelBuff, width, height, "r8g8b8a8")
                elif depth == 8:
                        pixelBuff = rapi.imageFromMortonOrder(pixelBuff,width,height)
                        texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 8, "r8g8b8a8")
                        
                elif depth == 4:
                        texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 4, "r8g8b8a8")
                
                
                dirName = rapi.getDirForFilePath(rapi.getInputName())
                outName = dirName + texName + ".png"
                texture = NoeTexture(texName, width, height, texData, noesis.NOESISTEX_RGBA32)
                #noesis.saveImageRGBA(outName,texture)
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
                self.boneIDList=[]
                self.boneNameList=[]                
                self.hAnimBoneIDList =[]
                self.hAnimBoneIndexList=[]                
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
                self.boneIDList.append(self.bs.readInt())
                boneCount = self.bs.readUInt()
                if boneCount:
                        self.hasAnim = 1
                        flags = self.bs.readInt()
                        keyFrameSize = self.bs.readInt()
                        for i in range(boneCount):
                                self.hAnimBoneIDList.append(self.bs.readInt())
                                self.hAnimBoneIndexList.append(self.bs.readInt())
                                boneType = self.bs.readInt()
        def rUserDataPLG(self,index):
                numSet = self.bs.readInt()
                boneName = "Dummy"+str(index)
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
                                self.boneNameList.append("Root")
                        else:
                                self.boneNameList.append("Dummy"+str(index))
        def rFrameExtList(self):
                for i in range(self.frameCount):
                        self.rFrameExt(i)
        
        def readBoneList(self):
                self.rFrameListStruct()
                self.rFrameExtList()
                bones=[]
                for i in range(self.frameCount):
                        boneIndex = self.boneIndexList[i]
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
                oldBoneIndexList = [0]*(self.frameCount-1)
                oldBonePrtIDlist =[0]*(self.frameCount-1)
                newBonePrtIdList = [0]*(self.frameCount-1)
                for i in range(self.frameCount-1):
                        oldBoneIndexList[self.boneIDList[i]] = i+1
                        oldBonePrtIDlist[self.boneIDList[i]] = self.bonePrtIdList[i+1]
                for i in range(self.frameCount-1):                        
                        oldPrtBoneIndex = oldBonePrtIDlist[self.boneIDList[i]] 
                        for j in range(self.frameCount-1):                                
                                if oldPrtBoneIndex == oldBoneIndexList[j]:                                
                                        newBonePrtIdList[self.boneIDList[i]] = j
                                        break
                                elif oldPrtBoneIndex == 0:
                                        newBonePrtIdList[self.boneIDList[i]] = -1
                                        break
                bones=[]
                for j in range(self.frameCount-1):                
                        boneIndex = j
                        boneName =  self.boneNameList[oldBoneIndexList[j]]
                        boneMat = self.boneMatList[oldBoneIndexList[j]]
                        bonePIndex = newBonePrtIdList[j]
                        bone = NoeBone(boneIndex, boneName, boneMat, None,bonePIndex)
                        bones.append(bone)
                for j in range(self.frameCount-1):
                        bonePIndex = newBonePrtIdList[j]
                        if(bonePIndex>-1):
                                prtMat=bones[bonePIndex].getMatrix()
                                boneMat = bones[j].getMatrix()                             
                                bones[j].setMatrix(boneMat * prtMat)
                        else:
                                prtMat=self.bones[0].getMatrix()
                                boneMat = bones[j].getMatrix()                             
                                bones[j].setMatrix(boneMat * prtMat)
                self.skinBones = bones
                
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
                        

                else:
                        skinStruct = rwChunk(self.bs)
                        unk_5 = self.bs.readInt()
                        boneCount = self.bs.readInt()
                        boneIndexList1=[]
                        boneIndexList2=[]
                        usedBoneCount = 0
                        for i in range(256):
                                boneIndex = self.bs.readInt()
                                if boneIndex > 0:
                                        boneIndexList1.append(boneIndex)
                                        usedBoneCount += 1
                        for i in range(boneCount):
                                boneIndex = self.bs.readInt()
                                boneIndexList2.append(boneIndex)
                        self.bs.seek((256-boneCount)*4,NOESEEK_REL)                        
                        unknown_type = self.bs.readInt()
                        maxWeightsPerVertex = self.bs.readInt()
                        unk1 = self.bs.readInt()
                        perVertDataSize = self.bs.readInt()
                        skinBoneIndexs=bytes()
                        skinBoneWeights=bytes()
                        for i in range(self.numVert):
                                for j in range(maxWeightsPerVertex):
                                        weight = self.bs.readUByte()/255.0
                                        wbytes = struct.pack('f',weight)
                                        skinBoneWeights += wbytes
                                for j in range(maxWeightsPerVertex):
                                        boneID = boneIndexList1[self.bs.readUShort() // 3]
                                        skinBoneIndexs += struct.pack('i',boneID)                                
                        rapi.rpgBindBoneIndexBuffer(skinBoneIndexs, noesis.RPGEODATA_INT, maxWeightsPerVertex*4 , maxWeightsPerVertex)
                        rapi.rpgBindBoneWeightBuffer(skinBoneWeights, noesis.RPGEODATA_FLOAT, maxWeightsPerVertex*4, maxWeightsPerVertex)
                                
                inverseBoneMats=[]
                for i in range(boneCount):
                        inverseBoneMats.append(NoeMat44.fromBytes(self.bs.readBytes(64)))                        
                self.bs.read('3f')
class rBinMeshPLG(object):
        def __init__(self,datas,matList,nativeFlag):
                self.bs = NoeBitStream(datas)
                self.matList = matList
                self.nativeFlag = nativeFlag
                self.matIdList = []
        def readFace(self):
                faceType = self.bs.readInt() # 1 = triangle strip
                numSplitMatID = self.bs.readUInt()
                indicesCount = self.bs.readUInt()
                for i in range(numSplitMatID):
                        faceIndices = self.bs.readUInt()
                        matID = self.bs.readUInt()
                        self.matIdList.append(matID)
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
        def __init__(self,datas,matList,matIdList,vertMat):
                self.bs = NoeBitStream(datas)
                self.matList = matList
                self.matIdList = matIdList
                self.vertMat = vertMat
        def readMesh(self):
                natvieStruct = rwChunk(self.bs)
                unk_5 = self.bs.readInt()
                vertexOffset = self.bs.tell() + self.bs.readInt()
                vertexUnk = self.bs.readShort()                
                materialCount = self.bs.readShort()
                unk_6 = self.bs.readInt()
                vertexCount = self.bs.readInt()
                perVertElementDataSize = self.bs.readInt()
                unk_flag = self.bs.readInt()
                matHeader_0 = self.bs.readInt()
                matHeader_unk1 = self.bs.readInt()
                matHeader_unk2 = self.bs.readInt()
                matTristripsInfo = []
                for i in range(materialCount):
                        vertexCountStart = self.bs.readInt()
                        vertexCountEnd = self.bs.readInt()
                        tristripsCount = self.bs.readInt()
                        unknownCount = self.bs.readInt()
                        self.bs.seek(8,1)
                        info = materialTristripsInfo(vertexCountStart,vertexCountEnd,tristripsCount,unknownCount)
                        matTristripsInfo.append(info)
                padLen = 16-((12+materialCount*24)%16)
                self.bs.seek(padLen,1)
                faceOffset = self.bs.tell()
                
                self.bs.seek(vertexOffset)
                vertBuff = bytes()
                uvBuff = bytes()
                colorBuff = bytes()
                for i in range(vertexCount):
                        #vertBuff+=self.bs.readBytes(12)
                        vert = NoeVec3.fromBytes(self.bs.readBytes(12))
                        vert *= self.vertMat
                        vertBuff+=vert.toBytes()                        
                        colorBuff+=self.bs.readBytes(4)
                        uvBuff += self.bs.readBytes(8)
                rapi.rpgBindPositionBuffer(vertBuff, noesis.RPGEODATA_FLOAT,12)
                rapi.rpgBindUV1Buffer(uvBuff, noesis.RPGEODATA_FLOAT, 8)
                #rapi.rpgBindColorBuffer(colorBuff, noesis.RPGEODATA_UBYTE, 4, 4)
                self.bs.seek(faceOffset)
                for i in range(materialCount):
                        info = matTristripsInfo[i]
                        matID = self.matIdList[i]
                        matName = self.matList[matID].name
                        rapi.rpgSetMaterial(matName)
                        tristrips = self.bs.readBytes(info.tristripsCount * 2)
                        rapi.rpgCommitTriangles(tristrips, noesis.RPGEODATA_USHORT, info.tristripsCount, noesis.RPGEO_TRIANGLE_STRIP, 1)
                        if ((info.tristripsCount * 2) % 16):
                                padLen = 16 - ((info.tristripsCount * 2) % 16)
                                self.bs.seek(padLen,1)

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
                #geoExtDatas = self.bs.readBytes(geoExtHeader.chunkSize)
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
                #if nativeFlags==1:
                #        print("found native mesh")
                if haveSkin:
                        skin = rSkin(skinDatas,numVert,nativeFlags)
                        skin.readSkin()
                if haveBinMesh:
                        binMeshPLG = rBinMeshPLG(binMeshDatas,matList,nativeFlags)
                        binMeshPLG.readFace()
                if haveNavtiveMesh:
                        nativeDataPLG = rNativeDataPLG(nativeDatas,matList,binMeshPLG.matIdList,self.vertMat)
                        nativeDataPLG.readMesh()
                #rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, (numFace * 3), noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()                

