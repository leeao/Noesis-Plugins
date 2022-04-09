#Kingdom Under Fire II .vap model and textures Noesis Importer.
#By Allen
from inc_noesis import *

loadSKL = False         # False, True. Manually select skeleton files
loadSameNameSKL = True  # Auto load same directory same name *.hkx skeleton file
debugMode = False       # Remove the "_" symbol from bone names to match similar bones.

def registerNoesisTypes():
	handle = noesis.register("Kingdom Under Fire II .vap model and textures", ".vap")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, vapLoadModel)

	handle = noesis.register("Kingdom Under Fire II .hkx skeleton", ".hkx;.dat;.bak")
	noesis.setHandlerTypeCheck(handle, HKXCheckType)
	noesis.setHandlerLoadModel(handle, HKXLoadModel)
	noesis.logPopup()
	return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readInt()
        if idstring != 1:
            return 0
        return 1
def vapLoadModel(data, mdlList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()
        id1 = bs.readInt()
        id2 = bs.readInt()
        bones = -1
        if loadSameNameSKL:
            fullName = rapi.getInputName()
            fname = rapi.getExtensionlessName(fullName)  
            hkxSklFileName = fname + ".hkx"
            #print(hkxSklFileName)
            if rapi.checkFileExists(hkxSklFileName):
                sklData = rapi.loadIntoByteArray(hkxSklFileName)
                sklbs = NoeBitStream(sklData)
                bones = readSkeleton(sklbs)
        if loadSKL:
            sklData = rapi.loadPairedFile("skeleton file", "*.*")             
            if sklData: 
                sklbs = NoeBitStream(sklData)
                bones = readSkeleton(sklbs)

        #player mesh
        if id1 == 1 and id2 == 1:        
            texList = []
            matList = []
            numTex = bs.readInt()
            for i in range(numTex):
                hashID = bs.readInt64()
                fileIndex = bs.readInt()
                unk = bs.readInt()
                
                width  = bs.readShort()
                height = bs.readShort()
                unkFlag = bs.readShort()
                texType = bs.readShort()
                pixelDataSize = bs.readInt()
                texData = bs.readBytes(pixelDataSize)
                texFormat = 0
                if texType == 0:
                    texFormat = noesis.NOESISTEX_DXT1
                elif texType == 4:
                    texFormat = noesis.NOESISTEX_DXT5
                elif texType == 133:
                    texData = rapi.imageDecodeRaw(texData,width,height,"R8A8")
                    texFormat = noesis.NOESISTEX_RGBA32                  
                elif texType == 176:
                    texFormat = noesis.NOESISTEX_RGB24                
                else:
                    print("can't support format:",texType)
                if texFormat != 0:    
                    texture = NoeTexture(str(fileIndex), width, height, texData, texFormat)
                    texList.append(texture)
                    mat = NoeMaterial(str(fileIndex), str(fileIndex))
                    matList.append(mat)  
            meshMagic = bs.readInt()
            numMesh = bs.readInt()
            for i in range(numMesh):
                hashID = bs.readInt64()
                fileIndex = bs.readInt()
                unk = bs.readInt()
                dataSize = bs.readInt()
                fileIndex2 = bs.readInt()
                unk2 = bs.readInt()
                FT2_MESH_DESC = bs.readString()
                unk3 = bs.readInt()
                bbox = bs.read('6f')
                unk4 = bs.read('4I')
                meshName = str(bs.readBytes(bs.readInt()), encoding = "utf-8")
                rapi.rpgSetMaterial(matList[1].name)
                rapi.rpgSetName(meshName)
                
                maxWeightBoneNumber = bs.readInt()
                numVert = bs.readInt()
                numChunk = bs.readInt()
                chunkStart = bs.tell()
                for j in range(numChunk):
                    chunkType = bs.readInt()
                    dataCount = bs.readInt() % 4 + 1
                    dataStride = dataCount * 4
                    
                    if chunkType == 0:
                        positions = bs.seek(numVert * dataStride,NOESEEK_REL)
                        numFaceIdex = bs.readInt()
                        faceBuffer = bs.seek( numFaceIdex * 4,NOESEEK_REL)
                    elif chunkType == 1:
                        normals = bs.seek(numVert * dataStride,NOESEEK_REL)
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)
                    elif chunkType == 2:
                        unkData1 = bs.seek(numVert * dataStride,NOESEEK_REL) # tangent??
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)
                    elif chunkType == 3:
                        unkData2 = bs.seek(numVert * dataStride,NOESEEK_REL) # binormals??                       
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)                        
                    elif chunkType == 4:
                        uvs = bs.seek(numVert * dataStride,NOESEEK_REL)      
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)   
                    elif chunkType == 5:
                        weights = bs.seek(numVert * dataStride,NOESEEK_REL)      
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)   
                    elif chunkType == 6:
                        boneIDs = bs.seek(numVert * dataStride,NOESEEK_REL)      
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)          
                    else:
                        unkDatas = bs.seek(numVert * dataStride,NOESEEK_REL)  
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)  
                unk5 = bs.read('5I')
                numBones = bs.readInt()
                boneNames = []
                for b in range(numBones):                    
                    if debugMode:
                        boneNames.append(str(bs.readBytes(bs.readInt()), encoding = "utf-8").replace("_"," "))
                    else:
                        boneNames.append(str(bs.readBytes(bs.readInt()), encoding = "utf-8"))
                    
                unk6 = bs.readInt()
                meshEndOfs = bs.tell()

                if bones != -1:
                    rsl = getPlayerMeshBoneMap(boneNames,numBones,bones)
                    boneMapList = rsl[0]
                    rapi.rpgSetBoneMap(boneMapList)
                bs.seek(chunkStart) 
                for j in range(numChunk):
                    chunkType = bs.readInt()
                    dataCount = bs.readInt() % 4 + 1
                    dataStride = dataCount * 4
                    
                    if chunkType == 0:
                        positions = bs.readBytes(numVert * dataStride)
                        rapi.rpgBindPositionBuffer(positions, noesis.RPGEODATA_FLOAT, dataStride)
                        numFaceIdex = bs.readInt()
                        faceBuffer = bs.readBytes( numFaceIdex * 4)
                    elif chunkType == 1:
                        normals = bs.readBytes(numVert * dataStride)
                        rapi.rpgBindNormalBuffer(normals, noesis.RPGEODATA_FLOAT, dataStride)
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)
                    elif chunkType == 2:
                        unkData1 = bs.readBytes(numVert * dataStride) # tangent??
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)
                    elif chunkType == 3:
                        unkData2 = bs.readBytes(numVert * dataStride) # binormals??                       
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)                        
                    elif chunkType == 4:
                        uvs = bs.readBytes(numVert * dataStride)      
                        rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, dataStride)
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)   
                    elif chunkType == 5:
                        weights = bs.readBytes(numVert * dataStride)      
                        rapi.rpgBindBoneWeightBuffer(weights, noesis.RPGEODATA_FLOAT, dataStride, dataCount)
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)   
                    elif chunkType == 6:
                        boneIDs = bs.readBytes(numVert * dataStride)      
                        rapi.rpgBindBoneIndexBuffer(boneIDs, noesis.RPGEODATA_INT, dataStride, dataCount)
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL)          
                    else:
                        unkDatas = bs.readBytes(numVert * dataStride)  
                        numFaceIdex2 = bs.readInt()
                        bs.seek(numFaceIdex2 * 4,NOESEEK_REL) 
                bs.seek(meshEndOfs)

                rapi.rpgCommitTriangles(faceBuffer, noesis.RPGEODATA_INT, numFaceIdex, noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()
                mdl = rapi.rpgConstructModel()
                mdl.setModelMaterials(NoeModelMaterials(texList,matList))
                if bones != -1:
                    mdl.setBones(bones)
                mdlList.append(mdl)	
                rapi.rpgReset()
        #npc mesh    
        elif id1 == 1:
            bs.seek(4)
            bbox = bs.read('6f')
            numMesh = bs.readInt()
            meshVertInfo = []
            meshFaceInfoList = []
            for i in range(numMesh):
                unk1 = bs.readInt()
                vertexStartIndex = bs.readInt()
                meshNumFace = bs.readInt()
                numSubMesh = bs.readInt()
                
                vertCount = 0
                meshFaceInfo = []
                for j in range(numSubMesh):
                    unk2 = bs.readInt()
                    subMeshName = str(bs.readBytes(bs.readInt()), encoding = "utf-8")
                    subMeshNumFace = bs.readInt()
                    unk3 = bs.readInt()
                    numMat = bs.readInt()
                    for m in range(numMat):
                        unk4 = bs.readInt()
                        matStartFaceIndex = bs.readInt()
                        prevMatVertexCount = bs.readInt()
                        matNumVertices = bs.readInt() + 1
                        matNumFace = bs.readInt()
                        matID = bs.readInt()
                        parentBoneID = bs.readInt()
                        
                        meshFaceInfo.append([subMeshName+"_"+str(m),matStartFaceIndex,matNumFace])
                        vertCount += matNumVertices
                meshVertInfo.append([vertexStartIndex,vertCount])
                meshFaceInfoList.append(meshFaceInfo)
            numBones = bs.readInt()
            boneNames = []
            for b in range(numBones):
                if debugMode:
                    boneNames.append(str(bs.readBytes(bs.readInt()), encoding = "utf-8").replace("_"," "))
                else:
                    boneNames.append(str(bs.readBytes(bs.readInt()), encoding = "utf-8"))
            numBoneIDChunk = bs.readInt()
            boneIDChunk = []
            for b in range(numBoneIDChunk):
                boneIDList = []
                numBoneID = bs.readInt()
                for v in range(numBoneID):
                    boneIDList.append(bs.readInt())
                boneIDChunk.append(boneIDList)
            if bones !=-1 :
                rsl = getBoneMap(boneNames,len(boneIDChunk[0]),boneIDChunk[0],bones)
                if rsl[1] == len(boneIDChunk[0]):
                    boneMapList = rsl[0]
                else:
                    print("Skeleton file is wrong, please change skeleton!")
                    boneMapList = -1

            unk2i = bs.read('2I')
            meshFormatBits = bs.readInt()
            unk3 = bs.readInt()
            vertexStride = bs.readInt()
            numVert = bs.readInt()
            unk4 = bs.readInt()
            vertexBuffer = bs.readBytes(numVert*vertexStride)
            unk5 = bs.readInt()
            unk6 = bs.readInt()
            unk7 = bs.readInt()
            unk8 = bs.readInt()
            numFaceIdex = bs.readInt()
            unk9 = bs.readInt()
            faceBuffer = bs.readBytes(numFaceIdex*2)
            
            for i in range(numMesh):
                if bones != -1 and boneMapList != -1:
                    rapi.rpgSetBoneMap(boneMapList)
                vertbuffer = bytearray(meshVertInfo[i][1]*vertexStride)
                vertbuffer[0:meshVertInfo[i][1]*vertexStride] = vertexBuffer[meshVertInfo[i][0]*vertexStride:meshVertInfo[i][0]*vertexStride+meshVertInfo[i][1]*vertexStride]
                
                rapi.rpgBindPositionBufferOfs(vertbuffer,noesis.RPGEODATA_FLOAT,vertexStride,0)
                rapi.rpgBindNormalBufferOfs(vertbuffer,noesis.RPGEODATA_UBYTE,vertexStride,12)
                rapi.rpgBindUV1BufferOfs(vertbuffer,noesis.RPGEODATA_HALFFLOAT,vertexStride,20)
                if vertexStride > 24:
                    
                    '''
                    if bones != -1 and boneMapList != -1:
                        numData = len(vertbuffer) // 32
                        newBneIdBuf = bytearray(numData*4)
                        for v in range(numData):
                            srcBIDs = noeUnpack('4B',vertbuffer[v*32+24:v*32+28])                            
                            for j in range(4):
                                newBneIdBuf[v*4+j] = boneMapList[srcBIDs[j]]
                        rapi.rpgBindBoneIndexBuffer(newBneIdBuf,noesis.RPGEODATA_UBYTE,4,4)
                    else:
                        rapi.rpgBindBoneIndexBufferOfs(vertbuffer,noesis.RPGEODATA_UBYTE,vertexStride,24,4)
                    '''
                    rapi.rpgBindBoneIndexBufferOfs(vertbuffer,noesis.RPGEODATA_UBYTE,vertexStride,24,4)
                    rapi.rpgBindBoneWeightBufferOfs(vertbuffer,noesis.RPGEODATA_UBYTE,vertexStride,28,4)
                    
                
                meshFaceInfo = meshFaceInfoList[i]
                for j in range(len(meshFaceInfo)):
                    rapi.rpgSetName(meshFaceInfo[j][0])
                    rapi.rpgSetMaterial(meshFaceInfo[j][0])
                    
                    faceBuff = bytearray(meshFaceInfo[j][2]*6)
                    faceBuff[0:meshFaceInfo[j][2]*6] = faceBuffer[meshFaceInfo[j][1]*2:meshFaceInfo[j][1]*2+meshFaceInfo[j][2]*6]
                    
                    rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, meshFaceInfo[j][2]*3, noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()
                mdl = rapi.rpgConstructModel()  
                if bones != -1 and boneMapList != -1:                    
                    mdl.setBones(bones)                              
                mdlList.append(mdl)	
                rapi.rpgReset()
        return 1
def getBoneMap(boneNames,numUsedBones,usedBoneIDs,bones):
    boneMapList = [0] * numUsedBones
    matchCount = 0
    for i in range(numUsedBones):
        usedBoneName = boneNames[usedBoneIDs[i]] 
        for j in range(len(bones)):
            bone = bones[j]
            if bone.name == usedBoneName:
                boneMapList[i] = bone.index
                matchCount += 1
                break
    
    return [boneMapList,matchCount]
def getPlayerMeshBoneMap(boneNames,numUsedBones,bones):
    boneMapList = [0] * numUsedBones
    matchCount = 0
    for i in range(numUsedBones):
        usedBoneName = boneNames[i] 
        for j in range(len(bones)):
            bone = bones[j]
            if bone.name == usedBoneName:
                boneMapList[i] = bone.index
                matchCount += 1
                break
    
    return [boneMapList,matchCount]


#HKX format reference Thanks Zee 
#https://github.com/CucFlavius/Zee-010-Templates/blob/main/Havok_HKX.bt

def HKXCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readInt()
        if idstring != -894431970:
            return 0
        return 1
    
def HKXLoadModel(data, mdlList):  
    bs = NoeBitStream(data) 
    ctx = rapi.rpgCreateContext()
    bones = readSkeleton(bs)
    if bones != -1:         
        mdl = NoeModel()
        mdl.setBones(bones)
        mdlList.append(mdl)
    return 1
def readSkeleton(bs):
    bones = -1
    idstring = bs.readInt()
    if idstring != -894431970:    
        return -1
    sklOffset = getSkeletonOffset(bs)
    if sklOffset != -1:
        bs.seek(sklOffset)
        numParentID = readValue(bs)
        type = readValue(bs)
        parentIDList = []
        for i in range(numParentID):
            parentIDList.append(readSValue(bs))
            
        numBones = readValue(bs)
        bitFlag = bs.readByte()
        nameList = []
        for i in range(numBones):
            nameLen = readValue(bs)
            if debugMode:
                boneName = str(bs.readBytes(nameLen), encoding = "utf-8").replace("_"," ")
            else:
                boneName = str(bs.readBytes(nameLen), encoding = "utf-8")
            nameList.append(boneName)
            
        numData = readValue(bs)
        
        matrixList = []
        for i in range(numData):
 
            pos = NoeVec3.fromBytes(bs.readBytes(12))
            pw = bs.readFloat()
            
            q = NoeVec4.fromBytes(bs.readBytes(16))
            quat = NoeQuat([q[0],q[1],q[2],q[3]])

            scale = NoeVec3.fromBytes(bs.readBytes(12))
            sw = bs.readFloat()

            matrix = quat.toMat43(1)            
            matrix[3] = pos
            matrixList.append(matrix)
                        

        bones = []
        for i in range(numData):   
                boneIndex = i
                boneName =  nameList[i]
                boneMat = matrixList[i]
                bonePIndex = parentIDList[i]
                bone = NoeBone(boneIndex, boneName, boneMat, None,bonePIndex)
                bones.append(bone) 
        for i in range(numData):
                bonePIndex = parentIDList[i]
                if(bonePIndex>-1):
                        prtMat = bones[bonePIndex].getMatrix()
                        boneMat = bones[i].getMatrix()                             
                        bones[i].setMatrix(boneMat * prtMat)   
    return bones

def readValue(bs):
    
    inData = bs.readBytes(4)
    bs.seek(bs.tell()-4)

    if not (inData[0] & 128):
        bs.seek(bs.tell()+1)        
        return (inData[0] // 2)
    elif not (inData[1] & 128):
        bs.seek(bs.tell()+2)  
        value = (inData[0] & 127 | ((inData[1] & 127) << 7)) // 2
        return value
    else:
        bs.seek(bs.tell()+3)  
        value = (((inData[0] & 127 |  ((inData[1] & 127) << 7)) & 16383 | ((inData[2] & 127) << 14)) & 4028628991) // 2
        return value
#signed
def readSValue(bs):
    
    v1 = bs.readByte()
    value = (v1 >> 1) & 0x7FFFFFBF
    v3 = v1 & 1
    v4 = 6
    if v1 < 0:
        v11 = -1
        while v11 < 0:
            v11 = bs.readUByte()
            v5 = (v11 & 0x7f) << v4
            v4 += 7
            value |= v5
        value -= 0x7FFFFF80
    if v3:
        value *= -1
    return value
        
def readString(bs):
    outStr = ""
    temp = bs.readUByte()   
    while temp > 31 and temp < 127:        
        if temp > 31 and temp < 127:            
            outStr += chr(temp)
            temp = bs.readUByte()
        else:
            break
    return outStr
def getSkeletonOffset(bs):
   
    endOfs = bs.getSize()
    while(bs.tell() < endOfs):
        curOfs = bs.tell()
        tempStr = readString(bs)
        if tempStr != "" and len(tempStr) >= 7:
            index = tempStr.find(".w32hkx",0)
            if index != -1:                
                return (curOfs + index + 7)                
    return -1

