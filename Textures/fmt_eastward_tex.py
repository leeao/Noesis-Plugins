#Eastward texture Noesis plugin.
#Author: Allen


from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Eastward Texture",".pgf")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
    noesis.logPopup()
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readInt() & 0xFFFFFF
        if idstring != 0x464750:
                return 0
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()
        idstring = bs.readInt()         #0x464750 PGF Pixpil Graphic Format
        unkLen1 = idstring >> 24
        fileSize = bs.readInt()
        bs.seek(unkLen1,NOESEEK_REL)
        dataSize = bs.readUInt()
        width = bs.readInt()
        height = bs.readInt()
        bpp = bs.readByte()
        unk2 = bs.readByte()
        unkLen2 = bs.readByte()
        unk3 = bs.readByte()
        bs.seek(unkLen2,NOESEEK_REL)
        
        decompressSize = width * height * bpp // 8
        datas = bs.readBytes(dataSize)
        datas = rapi.decompLZ4(datas,decompressSize)
        #rapi.exportArchiveFile("decmpdata.lz4",datas) #for test/check decompressed data.
                             
        texture = NoeTexture(rapi.getInputName(), width, height, datas, noesis.NOESISTEX_RGBA32)
        texList.append(texture)  
            
        return 1
def texWriteRGBA(data, width, height, bs):
        bs.writeBytes(data)
        return 1