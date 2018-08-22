import v4l2
import fcntl
import mmap
import select
import time

from logging import getLogger
l = getLogger(__name__)

from numpy import fromstring, uint16

class Camera:
    def __init__(self):
        self.W = 1920
        self.H = 1080
        #open
        l.debug("open")
        self.vd = open('/dev/video0', 'rb+', buffering=0)

        #querycap
        l.debug("querycap")
        cp = v4l2.v4l2_capability()
        fcntl.ioctl(self.vd, v4l2.VIDIOC_QUERYCAP, cp)

        #s_fmt
        l.debug("s_fmt")
        fmt = v4l2.v4l2_format()
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        fmt.fmt.pix.width = self.W
        fmt.fmt.pix.height = self.H
        fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_SBGGR10
        fmt.fmt.pix.field = v4l2.V4L2_FIELD_NONE
        fcntl.ioctl(self.vd, v4l2.VIDIOC_S_FMT, fmt) # set whatever default settings we got before

        fmt = v4l2.v4l2_format()
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        fcntl.ioctl(self.vd, v4l2.VIDIOC_G_FMT, fmt)
        self.framesize = fmt.fmt.pix.sizeimage

        #reqbufs
        l.debug("reqbufs")
        req = v4l2.v4l2_requestbuffers()
        req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        req.memory = v4l2.V4L2_MEMORY_MMAP
        req.count = 4
        fcntl.ioctl(self.vd, v4l2.VIDIOC_REQBUFS, req)

        self.buffers = []
        for ind in range(req.count):
            #querybufs
            buf = v4l2.v4l2_buffer()
            buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = v4l2.V4L2_MEMORY_MMAP
            buf.index = ind
            fcntl.ioctl(self.vd, v4l2.VIDIOC_QUERYBUF, buf)

            #mmap
            mm = mmap.mmap(self.vd.fileno(), buf.length, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=buf.m.offset)
            self.buffers.append(mm)

            #qbuf
            fcntl.ioctl(self.vd, v4l2.VIDIOC_QBUF, buf)

        #streamon
        l.debug("streamon")
        buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        fcntl.ioctl(self.vd, v4l2.VIDIOC_STREAMON, buf_type)

        #select
        l.debug("select")
        t0 = time.time()
        max_t = 1
        ready_to_read, ready_to_write, in_error = ([], [], [])
        while len(ready_to_read) == 0 and time.time() - t0 < max_t:
            ready_to_read, ready_to_write, in_error = select.select([self.vd], [], [], max_t)

    def get_frame(self):
        #dqbuf
        buf = v4l2.v4l2_buffer()
        l.debug("dqbuf")
        buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = v4l2.V4L2_MEMORY_MMAP
        fcntl.ioctl(self.vd, v4l2.VIDIOC_DQBUF, buf)

        l.debug("process")
        #convert to numpy array
        mm = self.buffers[buf.index]
        frame = mm.read(self.framesize)
        img = fromstring(frame, dtype=uint16).reshape(self.H, self.W)

        #save RAW
        #out = open("image.raw", "wb")
        #out.write(frame)
        #out.close()
        mm.seek(0)

        #qbuf
        l.debug("qbuf")
        fcntl.ioctl(self.vd, v4l2.VIDIOC_QBUF, buf)

        return img

    def close(self):
        #streamoff
        l.debug("streamoff")
        buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        fcntl.ioctl(self.vd, v4l2.VIDIOC_STREAMOFF, buf_type)

        #close
        l.debug("close")
        self.vd.close()
