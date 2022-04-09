#Thanks Turk645 blender version https://github.com/Turk645/PokemonMasters/
#Thanks MiniEmerald blender version https://github.com/MiniEmerald/PokemonMasters
#Noesis version By Allen
#support lmd model version : 1.33

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Pokemon Master model animation", ".lmd")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, lmdLoadModel)
    noesis.logPopup()
    return 1
def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.seek(0x4)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "LMD0":
        return 0
    return 1
    
def lmdLoadModel(data, mdlList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()

    chunkTable = checkChunk(bs)

    for c in chunkTable:
        if c == "mesh":            
            mdl = readModel(bs)
            mdlList.append(mdl)
        elif c == "animation":
            mdlData = rapi.loadPairedFile("model file",".lmd")
            mdlf = NoeBitStream(mdlData)
            mdlChunks = checkChunk(mdlf)
            isModel = checkModel(mdlChunks)
            if isModel:
                mdl = readModel(mdlf)
                mdlList.append(mdl)
            else:
                print("Parse failed! Please reselect model file!")
                return 0        
    
    return 1
def checkModel(chunkTable):
    isModel = False
    for c in chunkTable:
        if c == "mesh":
            isModel = True
            break
    return isModel
def checkChunk(bs):
    bs.seek(0x18)
    formatOffset = bs.tell() + bs.readUInt()
    bs.seek(formatOffset)
    chunkTableInfoOffset = bs.tell() + bs.readUInt()
    versionOffset = bs.tell() + bs.readUInt()
    bs.seek(chunkTableInfoOffset)
    numChunkOffset = bs.tell() + bs.readInt()
    numChunk = bs.readInt()
    chunkTableStart = bs.tell()
    chunkTable = []
    
    #bone,material,mesh,animation
    for i in range(numChunk):
        bs.seek(chunkTableStart+i*4)
        chunkNameOffset = bs.tell() + bs.readInt()
        bs.seek(chunkNameOffset)
        chunkNameSize = bs.readInt()
        chunkName = noeStrFromBytes(bs.readBytes(chunkNameSize))
        chunkTable.append(chunkName)
    return chunkTable
    
def readModel(bs):   
    bs.seek(0x34)
    boneDataOfs = bs.tell() + bs.readInt()
    boneList = buildSkeleton(bs,boneDataOfs)

    bs.seek(0x38)
    materialDataOfs = bs.tell() + bs.readInt()
    matList = parseMaterials(bs,materialDataOfs)

    bs.seek(0x48)
    meshCount = bs.readInt()
    meshList = []
    for x in range(meshCount):
        meshList.append(bs.tell() + bs.readInt())
    curMeshOffset = bs.tell()
    for x in meshList:
        readMeshChunk(bs,x,boneList)
    rapi.rpgSmoothNormals()
    mdl = rapi.rpgConstructModel()
    mdl.setBones(boneList)
    rapi.rpgReset()
    return mdl

    
def readMeshChunk(bs,dataStart,boneList):

    bs.seek(dataStart + 7)
    vertChunkSize = bs.readUByte()

    bs.seek(dataStart + 8)
    modelNameOffset = bs.tell() + bs.readInt()
    model_material_NameOffset =  bs.tell() + bs.readInt() # G_body_a`M_ch0000_00_red_skin. split char '`' 
    unkOffset =  bs.tell() + bs.readInt()
    matrix44 = bs.readBytes(64)
    
    bs.seek(modelNameOffset)
    modelNameLen = bs.readInt()
    modelName = noeStrFromBytes(bs.readBytes(modelNameLen))

    bs.seek(dataStart + 0x14)
    materialNameOffset = bs.tell() + bs.readInt()
    bs.seek(materialNameOffset + 8)
    materialNameSize = bs.readInt()
    materialName = noeStrFromBytes(bs.readBytes(materialNameSize))

    bs.seek(dataStart + 0x58)
    weightBoneNameTableStart = bs.tell() + bs.readInt()


    bs.seek(dataStart + 0x5C)
    weightBoneMatrixTableStart = bs.tell() + bs.readInt() # weight bone matrix4X4 data 64bytes

    
    BBox = bs.read('6f')
    
    #GetWeight Paint Names
    weightBoneNameTable = []
    bs.seek(weightBoneNameTableStart)
    weightBoneCount = bs.readInt()

    for x in range(weightBoneCount):
        bs.seek(weightBoneNameTableStart+ x*4 + 4)
        weightBoneNameOffset = bs.tell() + bs.readUInt()
        bs.seek(weightBoneNameOffset)
        weightBoneNameSize = bs.readInt()
        weightBoneName = noeStrFromBytes(bs.readBytes(weightBoneNameSize))
        weightBoneNameTable.append(weightBoneName)

    bs.seek(dataStart + 0x78)
    faceCount = bs.readUInt()
    faceChunkSizeOffset = bs.tell() + bs.readInt()
    unknownChunkOffset = bs.tell() + bs.readInt() #per data 16bytes * unknownCount
    bs.seek(dataStart + 0x84)
    vertCount = bs.readUInt()

    bs.seek(8,1)
    sizeTest = vertCount * vertChunkSize
    if sizeTest < 0x100:
        size = 1
        vertSize = noeUnpack("B",bs.readBytes(size))[0]
    elif sizeTest < 0x10000:
        size = 2
        vertSize = noeUnpack("H",bs.readBytes(size))[0]
    else:
        size = 4    
        vertSize = noeUnpack("L",bs.readBytes(size))[0]
    vertOffset = bs.tell()

    #Read Vertex
    vertBuffer = bs.readBytes(vertCount*vertChunkSize)
    rapi.rpgBindPositionBufferOfs(vertBuffer, noesis.RPGEODATA_FLOAT, 40,0)    
    rapi.rpgBindUV1BufferOfs(vertBuffer, noesis.RPGEODATA_HALFFLOAT, 40,16)
    #rapi.rpgBindBoneIndexBufferOfs(vertBuffer, noesis.RPGEODATA_UBYTE, 40, 20,4)
    rapi.rpgBindBoneWeightBufferOfs(vertBuffer, noesis.RPGEODATA_FLOAT, 40, 24,4)
    weightBoneIDs = bytes()
    for b in range(vertCount):
        boneIDs = noeUnpack("BBBB",vertBuffer[(b*40+20):(b*40+20)+4])
        weights = noeUnpack("ffff",vertBuffer[(b*40+24):(b*40+24)+16])
        tempBoneIDs =[]
        for j in range(4):
            for bi in range(len(boneList)):
                if weightBoneNameTable[boneIDs[j]] == boneList[bi].name:
                    if weights[j] > 0:
                        tempBoneIDs.append(bi)
                    else:
                        tempBoneIDs.append(0)
                    continue
        weightBoneIDs += noePack("BBBB",tempBoneIDs[0],tempBoneIDs[1],tempBoneIDs[2],tempBoneIDs[3])
    rapi.rpgBindBoneIndexBuffer(weightBoneIDs, noesis.RPGEODATA_UBYTE, 4,4)

    if size == 1:
        unknownSize = 2
    else:
        unknownSize = 4     
    bs.seek(vertOffset + vertSize + size + unknownSize)
    unknownCount = bs.readInt()
    bs.seek(0x10 * unknownCount, 1)
    sizeTest = bs.readInt()
    if faceCount < 0x100:
        size = 1
        faceSize = noeUnpack("B",bs.readBytes(size))[0]
    elif faceCount < 0x10000:
        size = 2
        faceSize = noeUnpack("H",bs.readBytes(size))[0]
    else:
        size = 4
        faceSize = noeUnpack("L",bs.readBytes(size))[0]
    
    if vertCount < 0x100:
        fSize = 1
        faceDataType = noesis.RPGEODATA_UBYTE
    elif vertCount < 0x10000:
        fSize = 2
        faceDataType = noesis.RPGEODATA_USHORT
    else:
        fSize = 4
        faceDataType = noesis.RPGEODATA_UINT
    faceOffset = bs.tell()

    #Read Faces
    faceBuffer = bs.readBytes(faceCount*fSize)
    
    rapi.rpgSetMaterial(materialName)
    rapi.rpgCommitTriangles(faceBuffer, faceDataType, faceCount, noesis.RPGEO_TRIANGLE, 1)
    rapi.rpgClearBufferBinds()


def buildSkeleton(bs,dataStart):
    bones = []
    
    bs.seek(dataStart+8)
    boneCount = bs.readInt()
    boneOffsetTable = []
    for i in range(boneCount):
        boneOffsetTable.append(bs.tell()+bs.readUInt())
    boneIndex = 0

    boneParentNames = []
    for x in boneOffsetTable:
        bs.seek(x)
        magic = bs.readInt()
        bs.seek(x + 4)
        nameOffset = bs.tell() + bs.readInt()
        bs.seek(nameOffset)
        boneNameLen = bs.readInt()
        boneName = noeStrFromBytes(bs.readBytes(boneNameLen))
        bs.seek(x + 8)
        boneMatrix = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
        bs.seek(x + 0x38)
        bonePos = noeUnpack('fff',bs.readBytes(4*3))
        bs.seek(x + 0x48)
        boneParentOffset = bs.tell()+bs.readUInt()
        bs.seek(boneParentOffset)
        boneParentNameLen = bs.readInt()
        boneParentName = noeStrFromBytes(bs.readBytes(boneParentNameLen))
        bone = NoeBone(boneIndex, boneName, boneMatrix, boneParentName)
        boneIndex += 1
        bones.append(bone)
        boneParentNames.append(boneParentName)

    for x in range(len(bones)):
        parentName = boneParentNames[x]
        for p in bones:
            if parentName == p.name:
                bones[x].setMatrix(bones[x].getMatrix()*p.getMatrix())
                continue
    return bones

def parseMaterials(bs,dataStart):
    matTable = []
    bs.seek(dataStart+4)
    matNameOfs = bs.tell() + bs.readInt()
    bs.seek(dataStart+12)
    textureCount = bs.readInt()
    texOfsTable = []
    for x in range(textureCount):
        texOfsTable.append(bs.tell() + bs.readInt())
    textures ={}
    for x in texOfsTable:
        bs.seek(x + 4)
        texFileRefOffset = bs.tell() + bs.readInt()
        texFileNameOffset = bs.tell() + bs.readInt()
        texFileMapOffset = bs.tell() + bs.readInt()
        bs.seek(texFileNameOffset)
        texFileNameSize = bs.readInt()
        texFileName = noeStrFromBytes(bs.readBytes(texFileNameSize))        

        bs.seek(texFileRefOffset)        
        texFileRefSize = bs.readInt()
        texFileRef = noeStrFromBytes(bs.readBytes(texFileRefSize))

        bs.seek(texFileMapOffset)
        texFileMapSize = bs.readInt()
        texFileMap = noeStrFromBytes(bs.readBytes(texFileMapSize))
        textures.update({texFileRef:texFileName})

    bs.seek(matNameOfs)
    materialCount = bs.readInt()
    matOffsetTable = []
    for x in range(materialCount):
        matOffsetTable.append(bs.tell() + bs.readInt())
    for x in matOffsetTable:
        bs.seek(x + 4)
        materialNameOffset = bs.tell() + bs.readInt()
        bs.seek(materialNameOffset)
        materialNameSize = bs.readInt()
        materialName = noeStrFromBytes(bs.readBytes(materialNameSize))

        bs.seek(x + 0x38)
        flag = bs.readInt()
        if flag == 0x40000000:
            bs.seek(x + 0x44)
        else:
            bs.seek(x + 0x40)
        texSlotCount = bs.readInt()
        texSlotsOffset = []
        texSlots = []

        for y in range(texSlotCount):
            texSlotsOffset.append(bs.tell() + bs.readInt())
        for texNode in texSlotsOffset:
            bs.seek(texNode)
            materialFileReferenceSize = bs.readInt()
            materialFileReferenceName = noeStrFromBytes(bs.readBytes(materialFileReferenceSize))
            texSlots.append(textures.get(materialFileReferenceName))
        for texName in texSlots:
            material = NoeMaterial(materialName, texName)
            matTable.append(material)
    return matTable
                                              
                
