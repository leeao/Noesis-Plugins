# ================================================================================
# Trapt (aka Kagero II: Dark Illusion) (PS2)
# Noesis script by Dave, 2021
# Modified version by Allen (Added Face, Bones, Skin, Fix vertex position)
# 
# ================================================================================

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Trapt",".smi")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    bs = NoeBitStream(data)
    magic = bs.readUInt()
    if magic != 0x20030818 :
        return 0
    return 1


# ================================================================================
# Read the model data
# ================================================================================

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    bs.seek(0x10)
    bone_count = bs.readUByte()
    tex_count = bs.readUByte()
    mesh_count = bs.readUShort()
    bone_table = bs.readUInt()
    mesh_table = bs.readUInt()
    texture_table = bs.readUInt()

    bones = []
    
    for b in range(bone_count):
        bs.seek(bone_table + (b * 0x70))
        boneMat = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()        
        parentIndex = bs.readShort()
        bs.seek(14,NOESEEK_REL)
        boneName = bs.readString()
        bone = NoeBone(b, boneName, boneMat, None, parentIndex)        
        bones.append(bone)
    for i in range(bone_count):  
            parentIndex = bones[i].parentIndex
            if parentIndex > -1 :
                    prtMat = bones[parentIndex].getMatrix()
                    boneMat = bones[i].getMatrix()                             
                    bones[i].setMatrix(boneMat * prtMat)
    texture_list = []

    for t in range(tex_count):
        bs.seek(texture_table + (t * 0x5c))
        tex_name = bs.readString()
        texture_list.append(tex_name)

    for m in range(mesh_count):
        bs.seek(mesh_table + (m * 0x2c))
        vert_start = bs.readUInt()
        norm_start = bs.readUInt()
        junk = bs.readUInt()
        uv_start = bs.readUInt()
        junk = bs.readUInt()
        skinBoneData_skipListOfs = bs.readUInt()
        boneIDs = bs.read('12B')			
        tex_num = bs.readUShort()
        flags = bs.readUShort()					# bit 0 = Positions, bit 1 = UVs, bit 2 = Normals, bit 5 and 6 = stride and per vertex has bones number
        vert_count = bs.readUShort()
                        
        if flags & 0x20:
            vert_stride = 32
            norm_stride = 16
        else:
            vert_stride = 16
            norm_stride = 8
            
        bs.seek(skinBoneData_skipListOfs)
        skipList = []
        skinBoneIDs = bytes()
        skinBoneIDList = []
        for i in range(vert_count):
            boneID4 = bs.readUShort()
            boneID3 = bs.readUShort() 
            boneID2 = bs.readUShort()
            boneID1 = bs.readUShort()  
            skipFlag = (boneID1 & 0x8000) == 0x8000
            skipList.append(skipFlag)            
            if flags & 0xF0:
                index = (boneID1 & 0x7fff) // 4
                b1 = boneIDs[index]
                skinBoneIDs += noePack('H',b1)
                skinBoneIDList.append(b1)
                if flags & 0x20:
                    index2 = boneID2 // 4 
                    b2 = boneIDs[index2] 
                    skinBoneIDs += noePack('H',b2)
                    skinBoneIDList.append(b2)
        if flags & 0x04:
            bs.seek(norm_start)
            normalsData = bs.readBytes(vert_count * norm_stride)
        bs.seek(vert_start)
        vertices = bytes()
        normals = bytes()
        skinWeights = bytes()
        for v in range(vert_count):
            vx = bs.readFloat()
            vy = bs.readFloat()
            vz = bs.readFloat()
            weight1 = bs.readFloat()
            skinWeights += noePack('f',weight1)            
            if vert_stride == 32:
                vx2 = bs.readFloat()
                vy2 = bs.readFloat()
                vz2 = bs.readFloat()
                weight2 = bs.readFloat()
                skinWeights += noePack('f',weight2)
            
            if (flags & 0xf0) == 0x10:
                parentIndex = skinBoneIDList[v]
                parentBoneMatrix = bones[parentIndex].getMatrix()
                vert = NoeVec3([vx,vy,vz])
                vert = parentBoneMatrix.transformPoint(vert)
                vertices += noePack("fff", vert[0], vert[1], vert[2]) 
                if flags & 0x04:                    
                    normalUnpack = noeUnpack('3h',normalsData[v*8:v*8+6])
                    normal = NoeVec3([normalUnpack[0]/32768.0,normalUnpack[1]/32768.0,normalUnpack[2]/32768.0])
                    normal = parentBoneMatrix.transformNormal(normal).normalize()
                    normals += noePack("fff", normal[0], normal[1], normal[2]) 
            elif (flags & 0xf0) == 0x30: 
                parentIndex = skinBoneIDList[v*2]
                parentBoneMatrix = bones[parentIndex].getMatrix()                   
                parentIndex2 = skinBoneIDList[v*2+1]
                parentBoneMatrix2 = bones[parentIndex2].getMatrix()  
                                 
                vert = NoeVec3([vx,vy,vz])
                vert2 = NoeVec3([vx2,vy2,vz2])

                if weight1 == 1.0:
                    blendVert = parentBoneMatrix.transformPoint(vert)
                    if flags & 0x04:                    
                        normalUnpack = noeUnpack('3h',normalsData[v*16:v*16+6])
                        normal = NoeVec3([normalUnpack[0]/32768.0,normalUnpack[1]/32768.0,normalUnpack[2]/32768.0])                        
                        normal = parentBoneMatrix.transformNormal(normal).normalize()
                        normals += noePack("fff", normal[0], normal[1], normal[2])    
                elif weight2 == 1.0:
                    blendVert = parentBoneMatrix2.transformPoint(vert2)
                    if flags & 0x04:                    
                        normalUnpack = noeUnpack('3h',normalsData[v*16+8:v*16+14])
                        normal = NoeVec3([normalUnpack[0]/32768.0,normalUnpack[1]/32768.0,normalUnpack[2]/32768.0])                        
                        normal = parentBoneMatrix2.transformNormal(normal).normalize()
                        normals += noePack("fff", normal[0], normal[1], normal[2]) 
                else:                    
                    blendVert1 = parentBoneMatrix.transformPoint(vert / weight1)
                    #blendVert2 = parentBoneMatrix2.transformPoint(vert2 / weight2)                     
                    #blendVert = (blendVert2+blendVert1) / 2
                    blendVert = blendVert1
                    if flags & 0x04:                    
                        normalUnpack = noeUnpack('3h',normalsData[v*16:v*16+6])
                        normal1 = NoeVec3([normalUnpack[0]/32768.0,normalUnpack[1]/32768.0,normalUnpack[2]/32768.0])                        
                        normal1 = parentBoneMatrix.transformNormal(normal1).normalize()
                        
                        normalUnpack2 = noeUnpack('3h',normalsData[v*16+8:v*16+14])
                        normal2 = NoeVec3([normalUnpack2[0]/32768.0,normalUnpack2[1]/32768.0,normalUnpack2[2]/32768.0])
                        normal2 = parentBoneMatrix2.transformNormal(normal2).normalize()
                        
                        normal = normal1 + normal2                        
                        normal = normal.normalize()
                        normals += noePack("fff", normal[0], normal[1], normal[2])                                            
                vertices += noePack("fff", blendVert[0], blendVert[1], blendVert[2])
            else:
                vertices += noePack("fff", vx, vy, vz)
                if flags & 0x04:                    
                    normalUnpack = noeUnpack('3h',normalsData[v*8:v*8+6])
                    normal = NoeVec3([normalUnpack[0]/32768.0,normalUnpack[1]/32768.0,normalUnpack[2]/32768.0]).normalize()
                    normals += noePack("fff", normal[0], normal[1], normal[2])                 

        rapi.rpgBindPositionBuffer(vertices, noesis.RPGEODATA_FLOAT, 12)
        if flags & 0x04:
            rapi.rpgBindNormalBuffer(normals, noesis.RPGEODATA_FLOAT, 12)
        if flags & 0x2:
            bs.seek(uv_start)
            uvs = bs.readBytes(vert_count * 8)
            rapi.rpgBindUV1Buffer(uvs, noesis.RPGEODATA_FLOAT, 8)
        if skinBoneIDs:
            if (flags & 0xf0) == 0x10:
                rapi.rpgBindBoneIndexBuffer(skinBoneIDs, noesis.RPGEODATA_SHORT, 2, 1)
                rapi.rpgBindBoneWeightBuffer(skinWeights, noesis.RPGEODATA_FLOAT, 4, 1) 
            elif (flags & 0xf0) == 0x30:
                rapi.rpgBindBoneIndexBuffer(skinBoneIDs, noesis.RPGEODATA_SHORT, 4, 2)
                rapi.rpgBindBoneWeightBuffer(skinWeights, noesis.RPGEODATA_FLOAT, 8, 2)    
        rapi.rpgSetName("Mesh_" + str(m))
        rapi.rpgSetMaterial(texture_list[tex_num] + ".tm2") 
        triangles = createTriList(skipList)
        rapi.rpgCommitTriangles(triangles, noesis.RPGEODATA_INT, len(triangles)//4, noesis.RPGEO_TRIANGLE, 1)                
        rapi.rpgClearBufferBinds()
        #print(m,texture_list[tex_num])
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)

    return 1
    
def createTriList(skipList):
    out = NoeBitStream()
    numVerts = len(skipList)
    startDir = 1
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
        f1 = f2
        f2 = f3         
    return out.getBuffer() 