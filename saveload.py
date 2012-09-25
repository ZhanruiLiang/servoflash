from pgui.root import Root, warn, hint
import os
import shutil
import cPickle
from servoboard import KeyFrame, ServoBoard

class SaveLoadError(Exception):
    pass

class SaveLoadManager:
    def __init__(self, servoc):
        self.servoc = servoc
        self.lastSave = None
        self.lastSaveData = None

    def load(self, filename):
        servoc = self.servoc
        try:
            with open(filename, 'rb') as f:
                data = cPickle.load(f)
            servosData = data['servos']
            servoc.remove_servo()
            for adata in servosData:
                keyFrames = adata['keyFrames']
                del adata['keyFrames']
                servo = ServoBoard(servoc, **adata)
                del servo.keyFrames[:]
                for a, dti in keyFrames:
                    servo.keyFrames.append(KeyFrame(dti, a))
                servoc.add_servo(servo)
            servoc.reset()
            servoc.mark_redraw()
            hint('load data from file "%s"' % filename)
            self.lastSave = filename
        except Exception as ex:
            raise SaveLoadError(ex)

    def save(self, filename):
        servoc = self.servoc
        try:
            if os.path.exists(filename):
                # file exist, backup
                self.backup_file(filename)
        except IOError as e:
            warn('%r' % e)
        try:
            data = self.gen_save_data()
            with open(filename, 'wb') as f:
                cPickle.dump(data, f, -1)
                self.lastSave = filename
                self.lastSaveData = data
        except Exception as ex:
            raise SaveLoadError(ex)
        hint('save data to file "%s"' % filename)

    def backup_file(self, filename):
        MaxBackupNum = 5
        files = []
        for i in xrange(MaxBackupNum):
            backupName = '.%s.~%d~' % (filename, i+1)
            if not os.path.exists(backupName):
                break
            files.append((os.stat(backupName).st_ctime, backupName))
        else:
            files.sort()
            backupName = files[0][1]
        shutil.copyfile(filename, backupName)
        hint('backup "%s" as "%s"' % (filename, backupName))

    def gen_save_data(self):
        servoc = self.servoc
        data = {}
        data['servos'] = servosData = []
        for servo in servoc.servos:
            adata = {}
            for attr in servoc.SERVO_ATTRS:
                adata[attr] = getattr(servo, attr)
            adata['keyFrames'] = [(kf.a, kf.dti) for kf in servo.keyFrames]
            servosData.append(adata)
        return data
