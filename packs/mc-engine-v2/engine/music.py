np.save('work/voice.npy',mix)
subprocess.run(['ffmpeg','-y','-v','error','-f','s16le','-ar',str(SR),'-ac','1','-i','-','-c:a','aac','work/mix.m4a'],input=(np.clip(mix,-1,1)*32767).astype('i2').tobytes())
