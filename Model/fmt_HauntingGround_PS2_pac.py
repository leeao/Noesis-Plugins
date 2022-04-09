from inc_noesis import *
def registerNoesisTypes():
	handle = noesis.register("Haunting Ground PS2 stage models", ".pac")
	noesis.setHandlerTypeCheck(handle, pacCheckType)
	noesis.setHandlerLoadModel(handle, pacLoadModel)
	return 1
def pacCheckType(data):
    bs = NoeBitStream(data)
    magic = bs.readUInt()
    if magic  != 0x800 :
            return 0
    return 1
def pacLoadModel(data, mdlList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()   
    
    unk1 = bs.readInt()
    unk2 = bs.readInt()
    unk3 = bs.readInt()        
    meshPackOfs = bs.readInt()
    
    light1Ofs = bs.readInt()
    light2Ofs = bs.readInt()
    cameraOfs = bs.readInt()
    unk4 = bs.readInt() 
    
    doorMeshPackOfs = bs.readInt()    
    texPackOfs = bs.readInt()
    text_Dialog_Ofs = bs.readInt() 
    meshPack2Ofs_2 = bs.readInt()
    
    meshPack2Ofs = bs.readInt()
    contrast_Color_Filters_Ofs = bs.readInt() 
    
    bs.seek(texPackOfs)
    numTex = bs.readInt()
    skipPadding(bs,16)
    baseTexOfs = bs.tell() + numTex * 16
    #texDict = {}
    texList = []
    for i in range(numTex):
        texFormat = bs.readInt()
        width = bs.readShort()
        height = bs.readShort()
        pixelSize = bs.readShort() << 4
        palSize = bs.readShort() << 4
        flag = bs.readInt()
        texOfs = (flag & 0xFFFFFF00) + baseTexOfs
        unkTexID = ((flag & 0xff) >> 4) - 1
        nextOfs = bs.tell()
        bs.seek(texOfs)
        pixelBuff = bs.readBytes(pixelSize)
        if palSize == 1024:
            palette = readPS2Palette(bs,256)
            palette = unswizzlePalette(palette)
            texData = rapi.imageDecodeRawPal(pixelBuff, palette, width, height, 8, "r8g8b8a8")                                                                          
        dirName = rapi.getDirForFilePath(rapi.getInputName())
        texName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getInputName()))+ "_"+ str(i)+".png"
        outName = dirName + texName + ".png"     
        #print(texName)
        #print(outName)
        texture = NoeTexture(texName, width, height, texData, noesis.NOESISTEX_RGBA32)    
        #noesis.saveImageRGBA(outName,texture)        
        #texDict[unkTexID] = texture
        texList.append(texture)
        bs.seek(nextOfs)
    
    bs.seek(meshPackOfs)
    meshOfs = bs.readInt()
    mesh2Ofs = bs.readInt()
    mesh3Ofs = bs.readInt()
    mesh4Ofs = bs.readInt()
    mesh5Ofs = bs.readInt()
    bs.seek(meshOfs+meshPackOfs)
    
    readMesh(bs,"mainmesh")
    
    if mesh2Ofs > 0:
        readMesh(bs,"main2mesh")
    if mesh3Ofs > 0:
        readMesh(bs,"main3mesh")
    if mesh4Ofs > 0:
        readMesh(bs,"main4mesh")
    if mesh5Ofs > 0:
        readMesh(bs,"main5mesh")
        
    bs.seek(doorMeshPackOfs)    
    doorMeshOfs = bs.readInt()
    doorMesh2Ofs = bs.readInt()
    #bs.seek(doorMeshOfs+doorMeshPackOfs)
    #readMesh(bs,"doormesh")
    #if doorMesh2Ofs > 0:
    #    readMesh(bs,"door2mesh")
    if meshPack2Ofs > 0:
        bs.seek(meshPack2Ofs)
        unk2 = bs.read('2i')
        count1 = bs.readInt()
        count2 = bs.readInt()
        unk3 = bs.read('3i')
        count3 = bs.readInt()
        ofsList1 = []
        ofsList2 = []
        for i in range(count1):
            ofsList1.append(bs.readInt())
        for i in range(count2):
            ofsList2.append(bs.readInt())
        for i in range(count1):
            bs.seek(meshPack2Ofs+ofsList1[i])
            readSecondaryMesh(bs,"secondaryMesh_")
        for i in range(count2):
            bs.seek(meshPack2Ofs+ofsList2[i])
            readSecondaryMesh(bs,"secondaryMesh2_")
    #rapi.rpgSmoothNormals()
    mdl = rapi.rpgConstructModel()
    matList = []
    for i in range(numTex):
            matName = "mtl" + str(i)
            tex = texList[i]
            material = NoeMaterial(matName, tex.name)
            matList.append(material)                    
    mdl.setModelMaterials(NoeModelMaterials(texList,matList))    
    
    mdlList.append(mdl)
    return 1   
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
def skipPadding(bs,alignBytes):
    paddingLen = alignBytes - (bs.tell() % alignBytes)
    if (bs.tell() % alignBytes) > 0:
        bs.seek(paddingLen,NOESEEK_REL)
def readFixedLenString(bs,length):
    #strBytes = bs.readBytes(length);
    #string = str(strBytes, encoding = "utf-8")
    baseOfs = bs.tell()    
    string = bs.readString()
    bs.seek(baseOfs+32)
    return string
def readSecondaryMesh(bs,meshType):
    baseOfs = bs.tell()
    meshName = readFixedLenString(bs,32)
    #print(meshName)
    translateFactor = NoeVec3.fromBytes(bs.readBytes(12))
    pad = bs.readInt()
    unkVec3 = NoeVec3.fromBytes(bs.readBytes(12))
    pad2 = bs.readInt()
    numVert = bs.readInt()
    matID = bs.readInt()
    unk = bs.readInt()
    uvOfs = bs.readInt()
    colorOfs = bs.readInt()
    vertOfs = bs.readInt()
    rapi.rpgSetName(meshType+meshName)
    rapi.rpgSetMaterial("mtl"+str(matID))    
            
    if vertOfs != 2:
        #print("name:",meshName,"numVert:",numVert,"material ID:",matID)
        bs.seek(uvOfs+baseOfs)
        uvs = bs.readBytes(numVert*8)
        rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
        bs.seek(colorOfs+baseOfs)
        colors = bytes()
        for i in range(numVert):
            colors += rgba32(bs.readUInt()) 
        rapi.rpgBindColorBuffer(colors, noesis.RPGEODATA_UBYTE, 4, 4)
        bs.seek(vertOfs+baseOfs)
        positions = bytes()
        skipList = []
        for i in range(numVert):
            positions += bs.readBytes(12)
            flag = (bs.readShort() & 0x8000) == 0x8000
            pad = bs.readShort()
            skipList.append(flag)              
        rapi.rpgBindPositionBuffer(positions, noesis.RPGEODATA_FLOAT, 12)    
        rapi.rpgSetPosScaleBias(None,translateFactor)     
        triangles = createTriList(skipList)
        rapi.rpgCommitTriangles(triangles, noesis.RPGEODATA_INT, len(triangles)// 4, noesis.RPGEO_TRIANGLE, 1)
        rapi.rpgClearBufferBinds()
    else:
        unk2i = bs.read('2i')
        unk2i_2 = bs.read('2i')
        unk5 = bs.readInt()
        zero = bs.readUInt()
        skipListOfs = colorOfs
        colorOfs = bs.readInt()
        vertOfs = bs.readInt()
        color2Ofs = bs.readInt()
        vert2Ofs = bs.readInt()
        bs.seek(uvOfs+baseOfs)
        uvs = bs.readBytes(numVert*4)
        uvs = getUV(uvs)
        rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
        bs.seek(colorOfs+baseOfs)
        colors = bytes()
        for i in range(numVert):
            colors += rgba32(bs.readUInt()) 
        rapi.rpgBindColorBuffer(colors, noesis.RPGEODATA_UBYTE, 4, 4)
        bs.seek(skipListOfs+baseOfs)
        skipList = []
        for i in range(numVert):
            flag = (bs.readByte() & 1) == 1
            skipList.append(flag)  
        bs.seek(vertOfs+baseOfs)
        positions = getVertex(bs.readBytes(numVert*6))            
        rapi.rpgBindPositionBuffer(positions, noesis.RPGEODATA_FLOAT, 12)        
        rapi.rpgSetPosScaleBias(None,translateFactor)    
        triangles = createTriList(skipList)
        rapi.rpgCommitTriangles(triangles, noesis.RPGEODATA_INT, len(triangles)// 4, noesis.RPGEO_TRIANGLE, 1)
        rapi.rpgClearBufferBinds()   
        '''
        #for vertex and color list 2
        rapi.rpgSetName(meshType+meshName+"_2")
        rapi.rpgSetMaterial("mtl"+str(matID))           
        bs.seek(color2Ofs+baseOfs)
        colors = bytes()
        for i in range(numVert):
            colors += rgba32(bs.readUInt())         
        bs.seek(vert2Ofs+baseOfs)
        positions = getVertex(bs.readBytes(numVert*6)) 
        rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgBindColorBuffer(colors, noesis.RPGEODATA_UBYTE, 4, 4)
        rapi.rpgBindPositionBuffer(positions, noesis.RPGEODATA_FLOAT, 12)    
        rapi.rpgSetPosScaleBias(None,translateFactor)          
   
        rapi.rpgCommitTriangles(triangles, noesis.RPGEODATA_INT, len(triangles)// 4, noesis.RPGEO_TRIANGLE, 1)
        rapi.rpgClearBufferBinds()
        '''
def readMesh(bs,meshType):
    endFlag = True
    count = 0 
    while(endFlag):
        numVert = bs.readInt()
        matID = bs.readInt()
        unk3 = bs.readInt()
        chunkSize = bs.readInt()
        #print("ID:",count,"numVert:",numVert,"material ID:",matID)
        if numVert != -1:
            rapi.rpgSetName(meshType+str(count))
            if(matID!=-1):
                rapi.rpgSetMaterial("mtl"+str(matID))
            else:
                rapi.rpgSetMaterial("shaderNoUV")
            count += 1
            matrix = NoeMat44.fromBytes(bs.readBytes(64)).transpose()  
            matrix = matrix.toMat43()      
            translateFactor = matrix[3]
            uvs = bs.readBytes(numVert*8)
            rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
            skipPadding(bs,16)
            colors = bytes()
            for i in range(numVert):
                colors += rgba32(bs.readUInt()) 
            rapi.rpgBindColorBuffer(colors, noesis.RPGEODATA_UBYTE, 4, 4)
            skipPadding(bs,16)
            positions = bytes()
            skipList = []
            for i in range(numVert):
                positions += bs.readBytes(12)
                flag = (bs.readShort() & 0x8000) == 0x8000
                pad = bs.readShort()
                skipList.append(flag)            
            #if meshType == "doormesh" or meshType == "door2mesh":
            #if meshType != "doormesh" and meshType != "door2mesh":
            rapi.rpgSetPosScaleBias(None,translateFactor)
            rapi.rpgBindPositionBuffer(positions, noesis.RPGEODATA_FLOAT, 12)
            triangles = createTriList(skipList)
            rapi.rpgCommitTriangles(triangles, noesis.RPGEODATA_INT, len(triangles)// 4, noesis.RPGEO_TRIANGLE, 1)
            rapi.rpgClearBufferBinds() 
        elif numVert == -1 and matID == -1:
            endFlag = False 
    #print(count)
def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t 
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
        else:
            faceDir = startDir
        f1 = f2
        f2 = f3         
    return out.getBuffer()      
def getVertex(vertData):
    bs = NoeBitStream(vertData)
    out = NoeBitStream()
    numVerts = len(vertData) // 6
    for i in range(numVerts):
        x = bs.readShort() / 128.0
        y = bs.readShort() / 128.0
        z = bs.readShort() / 128.0
        out.writeFloat(x)
        out.writeFloat(y)
        out.writeFloat(z)
    return out.getBuffer() 
def getUV(uvdata):
    uvin = NoeBitStream(uvdata)
    out = NoeBitStream()
    numVerts = len(uvdata) // 4
    for i in range(numVerts):
        u = uvin.readShort() / 32768.0
        v = uvin.readShort() / 32768.0
        out.writeFloat(u)
        out.writeFloat(v)
    return out.getBuffer()       