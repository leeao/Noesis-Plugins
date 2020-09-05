#Author: Allen
from inc_noesis import *
import os
def registerNoesisTypes():
    handle = noesis.register("Harry Potter And The Chamber Of Secrets PS2 .tpk textures", ".tpk")
    noesis.setHandlerTypeCheck(handle, tpkNoepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    handle = noesis.register("Harry Potter And The Chamber Of Secrets PS2 .hpm model", ".hpm")
    noesis.setHandlerTypeCheck(handle, hpmNoepyCheckType)
    noesis.setHandlerLoadModel(handle, hpmLoadModel)    
    return 1

def tpkNoepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "BIGF":
	    return 0
    return 1
def hpmNoepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "HPML":
	    return 0
    return 1
def hpmLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    magic = bs.readInt()
    version = bs.readShort()
    numBones = bs.readShort()
    numMaterials = bs.readShort()
    numMesh = bs.readShort()
    VifChunkSize = bs.readInt()  
    bs.seek(16+VifChunkSize)
    texNames = []
    matList = []
    for i in range(numMaterials):
        matInfo = readMatTexName(bs)
        texNames.append(rapi.getExtensionlessName(rapi.getLocalFileName(matInfo[0])))
        mat = NoeMaterial(texNames[i],texNames[i]+".png")
        #if matInfo[1] in [0,1,2]:
        #    mat.setFlags(noesis.NMATFLAG_TWOSIDED)       
        matList.append(mat)
    meshOffsetList = []
    meshMatIDList = []
    meshMatSkinBoneOfsList = []
    meshMatSubMeshInfo = []
    for i in range(numMesh):
        #print("curofs:",bs.tell())
        numMat = bs.readShort()
        unk = bs.readShort()
        boundBoxMin = NoeVec3.fromBytes(bs.readBytes(12))
        boundBoxMax = NoeVec3.fromBytes(bs.readBytes(12))
        meshName = readHpmString(bs)
        
        matIDList = []
        for j in range(numMat):
            matIDList.append(bs.readInt())
        meshMatIDList.append(matIDList)
        matOffsetList = []
        matSkinBoneOfsList = []
        matSubMeshInfo = []
        for j in range(numMat):
            meshType = bs.readByte() #3=static 11=skin
            numUnk = bs.readByte()
            zero = bs.readShort()
            numUnk2 = bs.readInt()
            numVert = bs.readInt()
            unk = bs.readInt()
            unk2 = bs.readInt()
            zero = bs.readInt()
            bs.seek(16,NOESEEK_REL)# 4 floats
            bs.seek(20,NOESEEK_REL)
            subMeshInfo = []
            subMeshInfo.append(meshType)
            subMeshInfo.append(numUnk)
            subMeshInfo.append(numUnk2)
            subMeshInfo.append(numVert)
            numType1 = bs.readByte()
            numType2 = bs.readByte()
            numType3 = bs.readByte()
            numType4 = bs.readByte()
            skinBoneIDOfs = bs.readInt()
            matSkinBoneOfsList.append(skinBoneIDOfs)
            offsetList = []
            if numType2:
                for n in range(numType2):
                    offset = bs.readInt()
                    size = bs.readInt()
                    offsetList.append([offset,size])
            if numType1:
                for n in range(numType1):
                    offset = bs.readInt()
                    size = bs.readInt()
                    offsetList.append([offset,size])                    
                    unk3 = bs.readInt()
                    unk4 = bs.readInt()
                    if numType2:
                        numData = bs.readInt()
                        bs.seek(numData*4,NOESEEK_REL)
            if numType3:
                bs.seek(32,NOESEEK_REL)

            matOffsetList.append(offsetList)
            matSubMeshInfo.append(subMeshInfo)
        meshOffsetList.append(matOffsetList)
        meshMatSkinBoneOfsList.append(matSkinBoneOfsList)
        meshMatSubMeshInfo.append(matSubMeshInfo)
        numData2 = bs.readInt()
        unk5 = bs.readInt()
        bs.seek(numData2*4,NOESEEK_REL)
        numData3 = bs.readInt()
        unk6 = bs.readInt()
        bs.seek(numData3*4,NOESEEK_REL)
    boneIndex = 0
    bones = []
    boneInfoList = []
    while (bs.tell() < bs.getSize()):
        #print("%x" %(bs.tell()))
        boneInfo = readBone(bs,boneIndex)
        boneIndex += 1
        bones.append(boneInfo[0])
        boneInfoList.append(boneInfo)
    numBones = len(bones)
    
    boneSkinIDs = []
    for i in range(numBones):
        boneSkinIDs.append(boneInfoList[i][3])
        
    skinBones = []
    for i in range(numBones):
        skinBones.append(bones[i])
    for i in range(numBones):
        skinBones[boneSkinIDs[i]] = bones[i]
    #find parent
    for i in range(numBones):
        for b in range(numBones):
            subBones = boneInfoList[b][1]
            if i == subBones[1]:
                bones[i].parentIndex = boneSkinIDs[b]
                continue

    #find slibing bone parent
    for i in range(numBones):
        for b in range(numBones):
            subBones = boneInfoList[b][1]          
            if i == subBones[0]:
                bones[i].parentIndex = bones[b].parentIndex
                continue
    for i in range(numBones):
        if bones[i].parentIndex != -1:
            bones[i].setMatrix(bones[i].getMatrix()*skinBones[bones[i].parentIndex].getMatrix())
    for i in range(numMesh):
        
        matOffsetList = meshOffsetList[i]
        matIDList = meshMatIDList[i]
        matSkinBoneOfsList = meshMatSkinBoneOfsList[i]
        matSubMeshInfo = meshMatSubMeshInfo[i]
        numMat = len(matIDList)
        numVert = 0
        numFace = 0
        for j in range(numMat):
            offsetList = matOffsetList[j]
            skinBoneOfs = matSkinBoneOfsList[j]
            subMeshInfo = matSubMeshInfo[j]
            vertDatas = []
            faceDatas = []
            UVDatas =[]
            normalDatas = []
            skinBoneIDs = []
            skinWeights = []
            colorDatas = []
            skinUsedBoneIDs = []
            
            if skinBoneOfs:
                bs.seek(16 + skinBoneOfs)            
                numBoneID = bs.readShort()
                for u in range(numBoneID):
                    boneID = bs.readShort()
                    skinUsedBoneIDs.append(boneID)
            parentBone = None
            parentBoneID = None
            for b in range(numBones):
                if len(boneInfoList[b][2]):
                    boneChildMeshID = boneInfoList[b][2][0]
                    if boneChildMeshID == i:
                        parentBone = bones[b]
                        parentBoneID = bones[b].index
                        continue            
    

            for o in range(len(offsetList)):
                
                bs.seek(16+offsetList[o][0])
                
                vifData =  bs.readBytes(offsetList[o][1])
                unpackData = rapi.unpackPS2VIF(vifData)
                
                for up in unpackData:
                    if up.numElems == 3 and up.elemBits == 32:
                            vertDatas.append(up.data)
                    elif up.numElems == 1 and up.elemBits == 8 :
                            triData = createTriList(up.data)
                            faceDatas.append(triData)                            
                    
                    elif up.numElems == 3 and up.elemBits == 8:
                            normals = getNormal(up.data)
                            normalDatas.append(normals)
                    
                    elif up.numElems == 2 and up.elemBits == 16:
                            newUVData = getUV(up.data)
                            UVDatas.append(newUVData)
                            
                    elif up.numElems == 4 and up.elemBits == 16:
                            vertSkinData = getVertexSkinBoneWeight(up.data,skinUsedBoneIDs)
                            boneIDBuffer = vertSkinData[0]
                            weightBuffer = vertSkinData[1]
                            skinBoneIDs.append(boneIDBuffer)
                            skinWeights.append(weightBuffer)
                    
                    elif up.numElems == 4 and up.elemBits == 8:
                            cin = NoeBitStream(up.data)
                            colorData = bytes()                            
                            for c in range(len(up.data) // 4):
                                colorData += rgba32(cin.readUInt())
                            colorDatas.append(colorData)
                            
            numVertBlock = len(vertDatas)
            for v in range(numVertBlock):
                
                vertBuffer = vertDatas[v]
                if parentBone != None:
                    vertBuffer = getVertex(vertBuffer,parentBone.getMatrix())
                    if len(skinBoneIDs) == 0:
                        vertSkinData = getSkinSingleBoneWeight(len(vertBuffer)//12,parentBoneID)
                        rapi.rpgBindBoneIndexBuffer(vertSkinData[0], noesis.RPGEODATA_INT, 4, 1)
                        rapi.rpgBindBoneWeightBuffer(vertSkinData[1], noesis.RPGEODATA_FLOAT, 4, 1)                        
                rapi.rpgBindPositionBuffer(vertBuffer, noesis.RPGEODATA_FLOAT, 12)
                
                UVData = UVDatas[v]
                rapi.rpgBindUV1Buffer(UVData, noesis.RPGEODATA_FLOAT, 8)
                if len(skinBoneIDs):
                    boneIDs = skinBoneIDs[v]
                    weights = skinWeights[v]
                    rapi.rpgBindBoneIndexBuffer(boneIDs, noesis.RPGEODATA_INT, 16, 4)
                    rapi.rpgBindBoneWeightBuffer(weights, noesis.RPGEODATA_FLOAT, 16, 4)
                if len(colorDatas):
                    colorData = colorDatas[v]                
                    rapi.rpgBindColorBuffer(colorData, noesis.RPGEODATA_UBYTE, 4, 4)
                faceBuffer = faceDatas[v]
                materialTexName = texNames[matIDList[j]]
                rapi.rpgSetMaterial(materialTexName)
                rapi.rpgCommitTriangles(faceBuffer, noesis.RPGEODATA_INT, (len(faceBuffer))//4, noesis.RPGEO_TRIANGLE, 1)
                rapi.rpgClearBufferBinds()
                numVert += len(vertBuffer)//12
                numFace += len(faceBuffer)//12
        #print(numVert,numFace)
    rapi.rpgOptimize()
    rapi.rpgSmoothNormals()
    mdl = rapi.rpgConstructModel()    
    mdl.setModelMaterials(NoeModelMaterials(None,matList))
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
def readHpmString(bs):
    hpmStr = bs.readString()
    strEndOfs = bs.tell()
    if (strEndOfs % 4):
        padLen = 4 - (strEndOfs % 4)
        bs.seek(padLen,NOESEEK_REL)
    return hpmStr

def readMatTexName(bs):
    bs.seek(64,NOESEEK_REL)
    unk = bs.readFloat()
    numTex = bs.readInt()
    temp = []
    for i in range(numTex):        
        matType = bs.readInt()        
        unk = bs.readInt()
        dispalyType = bs.readInt()        
        if matType == 5:
            bs.seek(4,NOESEEK_REL)
            bs.seek(64,NOESEEK_REL)
    texNames=[]
    for i in range(numTex):
        texName = readHpmString(bs)
        texNames.append(texName)
    if numTex:
        temp.append(texNames[0])
        temp.append(dispalyType)
    if not numTex:
        temp.append("NULL")
        temp.append(2)
    return temp

def getVertexSkinBoneWeight(data,skinUsedBoneIDs):
    vin = NoeBitStream(data)
    numVert = len(data) // 8
    boneIDs = bytes()
    weights = bytes()
    
    for i in range(numVert):
        weightCount = 0
        
        boneID1 = vin.readUByte() // 4        
        boneID1 = skinUsedBoneIDs[boneID1]        
        weight1 = vin.readUByte()       
        

        boneID2 = vin.readUByte() // 4        
        boneID2 = skinUsedBoneIDs[boneID2]        
        weight2 = vin.readUByte()

        boneID3 = vin.readUByte() // 4        
        boneID3 = skinUsedBoneIDs[boneID3]        
        weight3 = vin.readUByte()

        boneID4 = vin.readUByte() // 4        
        boneID4 = skinUsedBoneIDs[boneID4]        
        weight4 = vin.readUByte()
        if (weight1 + weight2 + weight3) < 255:
            weight4 = 255 - (weight1 + weight2 + weight3)
        count = 0
        if weight1 <= 255:
            boneIDs += noePack("i",boneID1)
            weights += noePack("f",weight1/255.0)
            weightCount += weight1
            count += 1
        if weightCount < 255 and weight2 < 255:
            boneIDs += noePack("i",boneID2)
            weights += noePack("f",weight2/255.0)
            weightCount += weight2
            count += 1
        if weightCount < 255 and weight3 < 255:
            boneIDs += noePack("i",boneID3)
            weights += noePack("f",weight3/255.0)
            weightCount += weight3
            count += 1
        if weightCount < 255 and weight4 < 255:
            boneIDs += noePack("i",boneID4)
            weights += noePack("f",weight4/255.0)
            weightCount += weight4
            count += 1
        if count < 4:
            for w in range(4-count):
                weights += noePack("f",0)
                boneIDs += noePack("i",0)
        
                      
    return [boneIDs,weights]

def getSkinSingleBoneWeight(numVerts,parentBoneID):
    boneIDs = bytes()
    weights = bytes()    
    for i in range(numVerts):
        weights += noePack("f",1.0)
        boneIDs += noePack("i",parentBoneID)
    return [boneIDs,weights]

    
def getVertex(vertBuffer,parentBoneMatrix):
    vin = NoeBitStream(vertBuffer)
    out = NoeBitStream()
    numVerts = len(vertBuffer) // 12
    for i in range(numVerts):
        vert = NoeVec3.fromBytes(vin.readBytes(12))
        vert *= parentBoneMatrix
        out.writeBytes(vert.toBytes())
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
    

def createTriList(flagData):
    
    vin = NoeBitStream(flagData)
    out = NoeBitStream()
    startFlag = vin.readByte()
    numVerts = startFlag & 0x7f
    unkFlag = startFlag & 0x80
    faceDir = -1
    f1 = 0
    f2 = 1

    for i in range (numVerts):        
        bitflag = vin.readByte()

        f3 = i
        skipFlag = bitflag & 0x80 #skip Isolated vertex
        filpFlag = bitflag & 0x7f #flip face normal

        if filpFlag == 0x20:
            faceDir = -1
        elif bitflag == 0:
            faceDir = 1
        if skipFlag != 0x80:
            if faceDir > 0:
                out.writeInt(f1)
                out.writeInt(f2)
                out.writeInt(f3)
            else:
                out.writeInt(f2)
                out.writeInt(f1)
                out.writeInt(f3)
            #faceDir *= -1
        f1 = f2
        f2 = f3
    return out.getBuffer()

def readFixedString(bs,fixedLen):
    strStartOfs = bs.tell()
    str = bs.readString()
    strEndOfs = bs.tell()
    padLen = fixedLen - (strEndOfs - strStartOfs)
    bs.seek(padLen,NOESEEK_REL)
    return str

def readBone(bs,boneIndex):
    boneInfo = []
    subBones = []
    childMeshIDs = []
    boneMatrix = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
    siblingID = bs.readShort()
    subID = bs.readShort()
    skinBoneID = bs.readInt()
    unk = bs.readInt()
    bMin = bs.read('3f')
    bMax = bs.read('3f')
    dataType = bs.readInt()
    boneName = readHpmString(bs)
    zero = bs.readInt()
    if (dataType == 1):
        childMeshID = bs.readInt()
        childMeshIDs.append(childMeshID)
        unkNum = bs.readInt()
        if unkNum == 1:
            unk1 = bs.readInt()
            unk2 = bs.readInt()
            numData = bs.readInt()
            for i in range(numData):
                numType1 = bs.readByte()
                numType2 = bs.readByte()
                numType3 = bs.readByte()
                numType4 = bs.readByte()
                unkOfs = bs.readInt()
                offsetList = []
                if numType1:
                    for n in range(numType1):
                        offset = bs.readInt()
                        size = bs.readInt()
                        offsetList.append([offset,size])
                if numType2:
                    for n in range(numType2):
                        offset = bs.readInt()
                        size = bs.readInt()
                        offsetList.append([offset,size])                    
                        unk3 = bs.readInt()
                        unk4 = bs.readInt()
                        if numType2:
                            numData = bs.readInt()
                            bs.seek(numData*4,NOESEEK_REL)
                if numType3:
                    bs.seek(32,NOESEEK_REL)
    elif dataType == 3:
        unkf = bs.read('4f')
        unk1 = bs.readInt()
        unk2 = bs.readByte()
        name2 = readFixedString(bs,35)        
    elif dataType == 5:
        unk = bs.readInt()
    bone = NoeBone(skinBoneID, boneName, boneMatrix, None,-1)
    boneInfo.append(bone)
    subBones.append(siblingID)
    subBones.append(subID)
    boneInfo.append(subBones)
    boneInfo.append(childMeshIDs)
    boneInfo.append(skinBoneID)
    return boneInfo

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    magic = bs.readInt()
    fileSize = bs.readInt()
    bs.setEndian(NOE_BIGENDIAN)
    numTex = bs.readInt()
    headSize = bs.readInt()
    for i in range(numTex):
        bs.setEndian(NOE_BIGENDIAN)
        offset = bs.readInt()
        size = bs.readInt()
        texName = bs.readString()
        nextOfs = bs.tell()

        bs.setEndian(NOE_LITTLEENDIAN)        
        bs.seek(offset)
        sshMagic = bs.readInt()
        sshFileSize = bs.readInt()
        unk = bs.readInt()
        unkStr = bs.readBytes(8)
        dataOffset = offset + bs.readInt()
        bs.seek(dataOffset)
        flag = bs.readInt()
        texType = flag & 0xff
        pixelSize = (flag >> 8) - 16
        width = bs.readShort()
        height = bs.readShort()
        zero = bs.readInt()
        unk2 = bs.readShort()
        unk3 = bs.readShort()
        pixel = bs.readBytes(pixelSize)
        if texType == 1:
            palSize = 64
        elif texType == 2:
            palSize = 1024
        if texType in [1,2]:
            palFlag = bs.readInt()
            palWidth = bs.readShort()
            palHeight = bs.readShort()
            numColors = bs.readShort()
            unk4 = bs.readShort()
            unk5 = bs.readShort()
            unk6 = bs.readShort()
            
            
            pals = bytes()
            for i in range(palSize // 4 ):
                pals += rgba32(bs.readUInt())
                
            if texType == 1:
                textureData = rapi.imageDecodeRawPal(pixel,pals,width,height,4,"r8g8b8a8")
                texList.append(NoeTexture(texName, width, height, textureData, noesis.NOESISTEX_RGBA32))
                
                outName = rapi.getDirForFilePath(rapi.getInputName())+ rapi.getExtensionlessName(texName[10:len(texName)]) + ".png"                
                if not rapi.checkFileExists(outName):
                    noesis.saveImageRGBA(outName,NoeTexture(texName, width, height, textureData, noesis.NOESISTEX_RGBA32))
                    
            elif texType == 2:
                pixel = rapi.imageUntwiddlePS2(pixel,width,height,8)
                textureData = rapi.imageDecodeRawPal(pixel,pals,width,height,8,"r8g8b8a8",noesis.DECODEFLAG_PS2SHIFT)
                texList.append(NoeTexture(texName, width, height, textureData, noesis.NOESISTEX_RGBA32))

                outName = rapi.getDirForFilePath(rapi.getInputName())+ rapi.getExtensionlessName(texName[10:len(texName)]) + ".png"                
                if not rapi.checkFileExists(outName):
                    noesis.saveImageRGBA(outName,NoeTexture(texName, width, height, textureData, noesis.NOESISTEX_RGBA32))
                    
        bs.seek(nextOfs)
    return 1
        

def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t

