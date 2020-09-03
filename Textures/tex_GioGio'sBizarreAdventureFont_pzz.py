#by Allen

#Decode GioGio's Bizarre Adventure nec20rg04.pzz font file

from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("GioGio's Bizarre Adventure font file", ".pzz")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.seek(4)
    idstring = bs.readInt()
    if idstring != 0x17e:
	    return 0
    return 1


def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    
    palette = []
    c1 = bytearray([255,255,255,0])
    c2 = bytearray([255,255,255,64])
    c3 = bytearray([255,255,255,192])
    c4 = bytearray([255,255,255,255])
    palette.append(c1)
    palette.append(c2)
    palette.append(c3)
    palette.append(c4)
    
    tile_w = 20
    tile_h = 20
    tile_size = tile_w * tile_h
    bpp = 2 #bits per pixel
    bpb = tile_size * bpp // 8 #bytes per block
    pixelDataSize = 0xbf200 - 0x800    
    fontCharCount = pixelDataSize // bpb
    width = 128 * tile_w
    height = fontCharCount // 128 * tile_h
    ntx = width // tile_w #128
    nty = height // tile_h #61
    
    bs.seek(0x800)

    #read 2bpp to 8bpp
    pixel = bytearray(width*height)
    for i in range(pixelDataSize):
        byteArray = decode2BPP(bs.readUByte())
        pixel[i*4:(i*4+4)]=byteArray[0:4]

    #untile
    pixel = tile2linear(pixel,ntx,nty,tile_h,tile_w)

    #get pixel buffer
    textureData = bytearray(width * height * 4)
    for i in range(width*height):
        textureData[i*4:(i+1)*4] = palette[pixel[i]]

    #display
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))   
    
    return 1

def decode2BPP(byte_index):
    t = bytearray(4)
    t[0] = (byte_index >> 6) & 0x3
    t[1] = (byte_index >> 4) & 0x3
    t[2] = (byte_index >> 2) & 0x3
    t[3] = byte_index & 0x3
    return t

def tile2linear(data,ntx,nty,tile_h,tile_w):
    width=ntx*tile_w
    height=nty*tile_h
    tilelst=[]
    tile_len=tile_w*tile_h
    for k in range(0,width*height,tile_len):
        tile = data[k:k+tile_len]
        tilelst.append(tile)
    nPixel_data=[]
    for a in range(nty):
        for b in range(tile_h):
            for c in range(ntx):
                for d in range(tile_w):
                    index = a*ntx+c
                    index_tile = b*tile_w+d
                    nPixel_data.append((tilelst[index][index_tile]))
    return nPixel_data
