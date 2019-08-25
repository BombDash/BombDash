import sys
import random
import weakref
import bs
import bsUtils
from bsVector import Vector
import bdUtils
import settings


class BombFactory(object):
    """
    category: Game Flow Classes

    Wraps up media and other resources used by bs.Bombs
    A single instance of this is shared between all bombs
    and can be retrieved via bs.Bomb.getFactory().

    Attributes:

       bombModel
          The bs.Model of a standard or ice bomb.

       stickyBombModel
          The bs.Model of a sticky-bomb.

       impactBombModel
          The bs.Model of an impact-bomb.

       landMinModel
          The bs.Model of a land-mine.

       tntModel
          The bs.Model of a tnt box.

       regularTex
          The bs.Texture for regular bombs.

       iceTex
          The bs.Texture for ice bombs.

       stickyTex
          The bs.Texture for sticky bombs.

       impactTex
          The bs.Texture for impact bombs.

       impactLitTex
          The bs.Texture for impact bombs with lights lit.

       landMineTex
          The bs.Texture for land-mines.

       landMineLitTex
          The bs.Texture for land-mines with the light lit.

       tntTex
          The bs.Texture for tnt boxes.

       hissSound
          The bs.Sound for the hiss sound an ice bomb makes.

       debrisFallSound
          The bs.Sound for random falling debris after an explosion.

       woodDebrisFallSound
          A bs.Sound for random wood debris falling after an explosion.

       explodeSounds
          A tuple of bs.Sounds for explosions.

       freezeSound
          A bs.Sound of an ice bomb freezing something.

       fuseSound
          A bs.Sound of a burning fuse.

       activateSound
          A bs.Sound for an activating impact bomb.

       warnSound
          A bs.Sound for an impact bomb about to explode due to time-out.

       bombMaterial
          A bs.Material applied to all bombs.

       normalSoundMaterial
          A bs.Material that generates standard bomb noises on impacts, etc.

       stickyMaterial
          A bs.Material that makes 'splat' sounds and makes collisions softer.

       landMineNoExplodeMaterial
          A bs.Material that keeps land-mines from blowing up.
          Applied to land-mines when they are created to allow land-mines to
          touch without exploding.

       landMineBlastMaterial
          A bs.Material applied to activated land-mines that causes them to
          explode on impact.

       impactBlastMaterial
          A bs.Material applied to activated impact-bombs that causes them to
          explode on impact.

       blastMaterial
          A bs.Material applied to bomb blast geometry which triggers impact
          events with what it touches.

       dinkSounds
          A tuple of bs.Sounds for when bombs hit the ground.

       stickyImpactSound
          The bs.Sound for a squish made by a sticky bomb hitting something.

       rollSound
          bs.Sound for a rolling bomb.
    """

    def getRandomExplodeSound(self):
        'Return a random explosion bs.Sound from the factory.'
        return self.explodeSounds[random.randrange(len(self.explodeSounds))]

    def __init__(self):
        """
        Instantiate a BombFactory.
        You shouldn't need to do this; call bs.Bomb.getFactory() to get a
        shared instance.
        """

        self.bombModel = bs.getModel('bomb')
        self.stickyBombModel = bs.getModel('bombSticky')
        self.impactBombModel = bs.getModel('impactBomb')
        self.landMineModel = bs.getModel('landMine')
        self.tntModel = bs.getModel('tnt')
        self.toxicModel = bs.getModel("toxic")
        self.poisonModel = bs.getModel("PoisonBottle")
        self.slipperModel = bs.getModel("slipper")
        self.dirtModel = bs.getModel("dirtBomb")
        self.bananaModel = bs.getModel("banana")
        self.shockWaveModel = bs.getModel("shockWaveBomb")
        self.petardModel = bs.getModel("petard")
        self.fireBottleModel = bs.getModel("fireBottle")
        self.elonMineModel = bs.getModel('elonMine')
        self.holyBombModel = bs.getModel('holyBomb')

        self.regularTex = bs.getTexture('bombColor')
        self.iceTex = bs.getTexture('bombColorIce')
        self.stickyTex = bs.getTexture('bombStickyColor')
        self.impactTex = bs.getTexture('impactBombColor')
        self.impactLitTex = bs.getTexture('impactBombColorLit')
        self.landMineTex = bs.getTexture('landMine')
        self.landMineLitTex = bs.getTexture('landMineLit')
        self.tntTex = bs.getTexture('tnt')
        self.forceTex = bs.getTexture('bombStickyForceColor')
        self.toxicTex = bs.getTexture("toxic")
        self.poisonTex = bs.getTexture("poison")
        self.slipperTex = bs.getTexture("slipper")
        self.dirtTex = bs.getTexture("dirtBomb")
        self.bananaTex = bs.getTexture("banana")
        self.shockWaveTex = bs.getTexture("shockWave")
        self.petardTex = bs.getTexture("petard")
        self.fireBottleTex = bs.getTexture("fireBottle")
        self.elonMineTex = bs.getTexture('achievementCrossHair')
        self.elonMineLitTex = bs.getTexture('circleNoAlpha')
        self.holyTex = bs.getTexture('yellow')

        self.hissSound = bs.getSound('hiss')
        self.tntSound = bs.getSound('tnt')
        self.debrisFallSound = bs.getSound('debrisFall')
        self.woodDebrisFallSound = bs.getSound('woodDebrisFall')

        self.explodeSounds = (bs.getSound('explosion01'),
                              bs.getSound('explosion02'),
                              bs.getSound('explosion03'),
                              bs.getSound('explosion04'),
                              bs.getSound('explosion05'))

        self.freezeSound = bs.getSound('freeze')
        self.fuseSound = bs.getSound('fuse01')
        self.activateSound = bs.getSound('activateBeep')
        self.warnSound = bs.getSound('warnBeep')
        self.toxicSound = bs.getSound("metall")
        self.poisonSound = bs.getSound("poisonBreak")
        self.shockWaveSound = bs.getSound("shockwaveImpact")
        self.healthBombSound = bs.getSound("healthPowerup")

        # set up our material so new bombs dont collide with objects
        # that they are initially overlapping
        self.bombMaterial = bs.Material()
        self.normalSoundMaterial = bs.Material()
        self.stickyMaterial = bs.Material()

        self.bombMaterial.addActions(
            conditions=((('weAreYoungerThan', 100),
                         'or', ('theyAreYoungerThan', 100)),
                         'and', ('theyHaveMaterial',
                                 bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision', 'collide', False)))

        # we want pickup materials to always hit us even if we're currently not
        # colliding with their node (generally due to the above rule)
        self.bombMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision', 'useNodeCollide', False)))
        
        self.bombMaterial.addActions(actions=('modifyPartCollision',
                                              'friction', 0.3))

        self.landMineNoExplodeMaterial = bs.Material()
        self.landMineBlastMaterial = bs.Material()
        self.landMineBlastMaterial.addActions(
            conditions=(
                ('weAreOlderThan', 200),
                 'and', ('theyAreOlderThan', 200),
                 'and', ('evalColliding',),
                 'and', (('theyDontHaveMaterial',
                          self.landMineNoExplodeMaterial),
                         'and', (('theyHaveMaterial',
                                  bs.getSharedObject('objectMaterial')),
                                 'or', ('theyHaveMaterial',
                                        bs.getSharedObject('playerMaterial'))))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.forseBombMaterial = bs.Material()
        self.forseBombMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyDontHaveMaterial',
                                 self.landMineNoExplodeMaterial),
                                'and', (('theyHaveMaterial',
                                         bs.getSharedObject('objectMaterial')),
                                        'or', ('theyHaveMaterial',
                                               bs.getSharedObject('playerMaterial'))))),
            actions=(('message', 'ourNode', 'atConnect', SetStickyMessage())))

        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                               'or',('theyHaveMaterial',
                                     bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.blastMaterial = bs.Material()
        self.blastMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', ExplodeHitMessage())))

        self.dinkSounds = (bs.getSound('bombDrop01'),
                           bs.getSound('bombDrop02'))
        self.stickyImpactSound = bs.getSound('stickyImpact')
        self.rollSound = bs.getSound('bombRoll01')

        # collision sounds
        self.normalSoundMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('footingMaterial')),
            actions=(('impactSound', self.dinkSounds, 2, 0.8),
                     ('rollSound', self.rollSound, 3, 6)))

        self.stickyMaterial.addActions(
            actions=(('modifyPartCollision', 'stiffness', 0.1),
                     ('modifyPartCollision', 'damping', 1.0)))

        self.stickyMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial')),
                        'or', ('theyHaveMaterial',
                               bs.getSharedObject('footingMaterial'))),
            actions=(('message', 'ourNode', 'atConnect', SplatMessage())))

class SplatMessage(object):
    pass

class ExplodeMessage(object):
    pass

class ImpactMessage(object):
    """ impact bomb touched something """
    pass

class SetStickyMessage(object):
    pass

class ArmMessage(object):
    pass

class WarnMessage(object):
    pass

class ExplodeHitMessage(object):
    "Message saying an object was hit"
    def __init__(self):
        pass

class Blast(bs.Actor):
    """
    category: Game Flow Classes

    An explosion, as generated by a bs.Bomb.
    """
    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0), blastRadius=2.0,
                 blastType='normal', blastColor=(1, 0.3, 0.1), sourcePlayer=None, 
                 hitType='explosion', hitSubType='normal', notShake=False, notScorch=False):
        """
        Instantiate with given values.
        """
        bs.Actor.__init__(self)
        
        factory = Bomb.getFactory()

        self.blastType = blastType
        self.sourcePlayer = sourcePlayer

        self.hitType = hitType;
        self.hitSubType = hitSubType;

        # blast radius
        self.radius = blastRadius

        # set our position a bit lower so we throw more things upward
        self.node = bs.newNode('region', delegate=self, attrs={
            'position': (position[0], position[1]-0.1, position[2]),
            'scale': (self.radius, self.radius, self.radius),
            'type': 'sphere',
            'materials': (factory.blastMaterial,
                          bs.getSharedObject('attackMaterial'))})

        bs.gameTimer(50, self.node.delete)

        # throw in an explosion and flash
        explosion = bs.newNode('explosion', attrs={
            'position': position,
            'velocity': (velocity[0], max(-1.0, velocity[1]), velocity[2]),
            'radius': self.radius,
            'big': (self.blastType == 'tnt')})

        if self.blastType == 'ice':
            explosion.color = (0, 0.05, 0.4)

        elif self.blastType == 'turret':
            explosion.color = (0.5, 0, 0)

        elif self.blastType == 'shockWave' or self.blastType == 'rail':
            explosion.color = (0.3, 0.3, 1)

        elif self.blastType == 'heal':
            explosion.color = (0.6, 0.3, 0.3)

        elif self.blastType == 'banana':
            explosion.color = (1, 1, 0)

        elif self.blastType == 'petard':
            explosion.color = (0.1, 1, 0.3)

        elif self.blastType == 'portal':
            explosion.color = (1, 1 ,1)

        else:
            explosion.color = blastColor

        if not self.blastType == 'rail': 
            bs.gameTimer(1000, explosion.delete)
        else:
            bsUtils.animate(explosion, 'radius',
                    {0: self.radius, 8000:0})
            bs.gameTimer(8000, explosion.delete)

        if not self.blastType in ['turret', 'heal', 'shockWave', 'rail',
                                  'giant', 'portal', 'colorBomb']:
            if self.blastType != 'ice':
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(1.0+random.random()*4),
                                  emitType='tendrils',tendrilType='thinSmoke')
            bs.emitBGDynamics(
                position=position, velocity=velocity,
                count=int(4.0+random.random()*4), emitType='tendrils',
                tendrilType='ice' if self.blastType == 'ice' else 'smoke')
            bs.emitBGDynamics(
                position=position, emitType='distortion',
                spread=1.0 if self.blastType == 'tnt' else 2.0)
        
        # and emit some shrapnel..
        if self.blastType == 'ice':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=30, spread=2.0, scale=0.4,
                                  chunkType='ice', emitType='stickers');

            bs.gameTimer(50, _doEmit) # looks better if we delay a bit

        elif self.blastType == 'sticky':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8),
                                  spread=0.7, chunkType='slime');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8),
                                  scale=0.5, spread=0.7, chunkType='slime');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=15, scale=0.6, chunkType='slime',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(6.0+random.random()*12),
                                  scale=0.8, spread=1.5, chunkType='spark');

            bs.gameTimer(50, _doEmit) # looks better if we delay a bit

        elif self.blastType == 'giant':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(30.0+random.random()*10),
                                  scale=1+random.random(), chunkType='rock');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(20.0+random.random()*10),
                                  scale=1+random.random(), chunkType='metal');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(8.0+random.random()*15),
                                  scale=0.8, spread=1.5, chunkType='spark');
                bs.emitBGDynamics(position=position, emitType='distortion',
                                  spread=5.0);
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(40.0+random.random()*10),
                                  emitType='tendrils', tendrilType='thinSmoke');

            bs.gameTimer(50, _doEmit)

        elif self.blastType == 'impact': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.8,
                                  chunkType='metal');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.4,
                                  chunkType='metal');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(8.0+random.random()*15), scale=0.8,
                                  spread=1.5, chunkType='spark');

            bs.gameTimer(50, _doEmit) # looks better if we delay a bit

        elif self.blastType == 'shockWave':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8),
                                  scale=0.8, chunkType='metal');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');

                f = bs.newNode('flash', attrs={
                    'position': position,
                    'size': 0.5,
                    'color': (0.6, 0.6, 1-random.random()*0.2)})

                bs.gameTimer(60, f.delete)

            bs.gameTimer(50, _doEmit)

        elif self.blastType == 'rail':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');

                f = bs.newNode('flash', attrs={
                    'position': position,
                    'size': 0.5,
                    'color': (0.6, 0.6, 1-random.random()*0.2)})
                bsUtils.animate(f, 'size',
                    {0: 0.5, 460:0})
                bs.gameTimer(460, f.delete)

            bs.gameTimer(50, _doEmit)
            
        elif self.blastType == 'petard':
            bs.emitBGDynamics(position=position, count=50,
                              emitType='tendrils', tendrilType='smoke')
            
        elif self.blastType == 'dirtBomb':
            def _doEmit():
                for i in xrange(80):
                    bdUtils.Clay(
                        position=(position[0]-1+random.random()*2,
                                  position[1]+random.random(),
                                  position[2]-1+random.random()*2),
                        velocity=(-2+random.random()*4,
                                  -2+random.random()*4,
                                  -2+random.random()*4),
                        bomb=True).autoRetain()

            bs.gameTimer(10, _doEmit)
            
        elif self.blastType == 'banana':
            def _doEmit():
                for i in xrange(10):
                    bdUtils.Clay(
                        position=(position[0]-1+random.random()*2,
                                  position[1]+random.random(),
                                  position[2]-1+random.random()*2),
                        velocity=(-2+random.random()*4,
                                  -2+random.random()*4,
                                  -2+random.random()*4),
                        banana=True,
                        bomb=True).autoRetain()

                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=1000, scale=2.5, chunkType='sweat',
                                  emitType='stickers')

            bs.gameTimer(15, _doEmit)

        elif self.blastType == 'holy':
            bs.emitBGDynamics(
                position=(position[0], position[1]+4, position[2]),
                velocity=(0, 0, 0),
                count=700,
                spread=0.7,
                chunkType='spark')

        elif self.blastType in ['heal', 'portal', 'turret']:
            pass

        else: # regular or land mine bomb shrapnel
            def _doEmit():
                if self.blastType != 'tnt':
                    bs.emitBGDynamics(position=position, velocity=velocity,
                                      count=int(4.0+random.random()*8),
                                      chunkType='rock');
                    bs.emitBGDynamics(position=position, velocity=velocity,
                                      count=int(4.0+random.random()*8),
                                      scale=0.5,chunkType='rock');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=30,
                                  scale=1.0 if self.blastType=='tnt' else 0.7,
                                  chunkType='spark', emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(18.0+random.random()*20),
                                  scale=1.0 if self.blastType == 'tnt' else 0.8,
                                  spread=1.5, chunkType='spark');

                # tnt throws splintery chunks
                if self.blastType == 'tnt':
                    def _emitSplinters():
                        bs.emitBGDynamics(position=position, velocity=velocity,
                                          count=int(20.0+random.random()*25),
                                          scale=0.8, spread=1.0,
                                          chunkType='splinter');

                    bs.gameTimer(10, _emitSplinters)
                
                # every now and then do a sparky one
                if self.blastType == 'tnt' or random.random() < 0.1:
                    def _emitExtraSparks():
                        bs.emitBGDynamics(position=position, velocity=velocity,
                                          count=int(10.0+random.random()*20),
                                          scale=0.8, spread=1.5,
                                          chunkType='spark');

                    bs.gameTimer(20, _emitExtraSparks)
                        
            bs.gameTimer(50, _doEmit) # looks better if we delay a bit

        if not self.blastType == 'turret':
            if self.blastType == 'ice':
                color = (0, 0.05, 0.4)

            elif self.blastType == "turret":
                color = (0.5, 0, 0)

            elif self.blastType == 'shockWave' or self.blastType == 'rail':
                color = (0.3, 0.3, 1)

            elif self.blastType == 'heal':
                color = (0.6, 0.3, 0.3)

            elif self.blastType == 'colorBomb':
                color = (random.random(),
                         random.random(),
                         random.random())

            elif self.blastType == 'banana':
                color = (1, 1, 0)

            elif self.blastType == 'petard':
                color = (0.1, 1, 0.3)

            elif self.blastType == 'portal':
                color = (1, 1, 1)

            else:
                color = blastColor

            light = bs.newNode('light', attrs={
                'position': position,
                'color': color,
                'volumeIntensityScale': 10.0})
        else:
            light = bs.newNode('light', attrs={
                'position': position,
                'color': (0.4, 0, 0),
                'volumeIntensityScale': 10.0})

        s = random.uniform(0.6, 0.9)
        scorchRadius = lightRadius = self.radius
        if self.blastType == 'tnt':
            lightRadius *= 1.4
            scorchRadius *= 1.15
            s *= 3.0

        elif self.blastType == 'turret':
            lightRadius *= 0.05
            scorchRadius *= 0.05
            s *= 0.05

        elif self.blastType == 'rail':
            lightRadius *= 0.4
            s *= 30

        elif self.blastType == 'petard':
            s *= 3.0

        if not self.blastType == 'rail': 
            iScale = 1.6
        else:
            iScale = 0.2
        
        if not self.blastType == 'rail':
            bsUtils.animate(light, 'intensity', {
                0: 2.0*iScale, int(s*20): 0.1*iScale,
                int(s*25): 0.2*iScale, int(s*50): 17.0*iScale, int(s*60): 5.0*iScale,
                int(s*80): 4.0*iScale, int(s*200): 0.6*iScale,
                int(s*2000): 0.00*iScale, int(s*3000): 0.0})
            bsUtils.animate(light, 'radius', {
                0: lightRadius*0.2, int(s*50): lightRadius*0.55,
                int(s*100): lightRadius*0.3, int(s*300): lightRadius*0.15,
                int(s*1000): lightRadius*0.05})
        else:
            bsUtils.animate(light, 'intensity', {
                0:17.0*iScale, int(s*60): 5.0*iScale,
                int(s*80): 4.0*iScale, int(s*200): 0.6*iScale,
                int(s*2000): 0.00*iScale, int(s*3000): 0.0})
            bsUtils.animate(light, 'radius', {
                0: lightRadius*0.6,
                int(s*1000): lightRadius*0.1})
        bs.gameTimer(int(s*3000), light.delete)

        # make a scorch that fades over time
        if not self.blastType in ['heal', 'shockWave', 'turret',
                                  'portal', 'colorBomb'] \
                and not notScorch:
            scorch = bs.newNode('scorch', attrs={
                'position': position,
                'size': scorchRadius*0.5,
                'big': (self.blastType == 'tnt')})

            if self.blastType == 'ice':
                scorch.color = (1, 1, 1.5)

            elif self.blastType == 'banana':
                scorch.color = (1, 1, 0)

            else:
                scorch.color = (random.random(),
                                random.random(),
                                random.random())

            bsUtils.animate(scorch, 'presence',
                {3000: 1, 13000: 0})

            bs.gameTimer(13000, scorch.delete)

        if self.blastType == 'ice':
            bs.playSound(factory.hissSound, position=light.position)
            
        p = light.position
        if not self.blastType == 'turret' and not self.blastType == 'heal' and not self.blastType == 'holy' and not self.blastType == 'rail':
            bs.playSound(factory.getRandomExplodeSound(), position=p)
            bs.playSound(factory.debrisFallSound, position=p)

        elif self.blastType == 'holy':
            bs.playSound(factory.tntSound, position=p)

        elif self.blastType == 'heal':
            bs.playSound(bs.getSound('healthBomb'), position=p)

        if not notShake:
            if self.blastType == 'tnt':
                bs.shakeCamera(intensity=5.0)
            elif self.blastType == 'turret':
                bs.shakeCamera(intensity=0.0)
            else:
                bs.shakeCamera(intensity=1.0)

        # tnt is more epic..
        if self.blastType == 'tnt':
            bs.playSound(factory.tntSound, position=p)
            def _extraBoom():
                bs.playSound(factory.getRandomExplodeSound(), position=p)

            bs.gameTimer(250, _extraBoom)
            def _extraDebrisSound():
                bs.playSound(factory.debrisFallSound, position=p)
                bs.playSound(factory.woodDebrisFallSound, position=p)

            bs.gameTimer(400, _extraDebrisSound)

    def handleMessage(self, m):
        self._handleMessageSanityCheck()
        
        if isinstance(m, bs.DieMessage):
            self.node.delete()

        elif isinstance(m, ExplodeHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            if node is not None and node.exists():
                t = self.node.position

                # new
                mag = 2000.0
                if self.blastType == 'ice': mag *= 0.5
                elif self.blastType == 'forceBomb': mag *= 0.25
                elif self.blastType == 'landMine': mag *= 2.5
                elif self.blastType == 'tnt': mag *= 2.0
                elif self.blastType == 'elonMine': mag *= 1.0
                elif self.blastType == 'holy': mag *= 2.0

                node.handleMessage(bs.HitMessage(
                    pos=t,
                    velocity=(0,0,0),
                    magnitude=mag,
                    hitType=self.hitType,
                    hitSubType=self.hitSubType,
                    radius=self.radius,
                    sourcePlayer=self.sourcePlayer))
                if self.blastType == "ice":
                    bs.playSound(Bomb.getFactory().freezeSound, 10, position=t)
                    node.handleMessage(bs.FreezeMessage())

        else:
            bs.Actor.handleMessage(self, m)

class Bomb(bs.Actor):
    """
    category: Game Flow Classes
    
    A bomb and its variants such as land-mines and tnt-boxes.
    """

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0), bombType='normal',
                 blastRadius=2.0, sourcePlayer=None, owner=None, modelSize=1,
                 notShake=False, napalm=False, notSound=False):
        """
        Create a new Bomb.
        
        bombType can be 'ice','impact','landMine','normal','sticky', or 'tnt'.
        Note that for impact or landMine bombs you have to call arm()
        before they will go off.
        """
        bs.Actor.__init__(self)
        self.slipperPlanted = False
        self.aim = None
        self.slipperThree = False
        self.slipperThreeDropped = False
        self.napalm = napalm
        self.notSound = notSound
        self.notShake = notShake

        factory = self.getFactory()

        if not bombType in ('ice', 'impact', 'landMine',
                            'normal', 'sticky', 'tnt',
                            'forceBomb', 'toxic', 'poison',
                            'slipper', 'dirtBomb', 'heal',
                            'banana', 'shockWave', 'petard',
                            'fireBottle', 'portal', 'holy',
                            'airstrike', 'elonMine', 'colorBomb'):
            raise Exception('invalid bomb type: '+bombType)

        self.bombType = bombType

        self._exploded = False

        if self.bombType == 'sticky' or self.bombType == 'forceBomb':
            self._lastStickySoundTime = 0

        self.blastRadius = blastRadius
        if self.bombType == 'ice': self.blastRadius *= 1.2
        elif self.bombType == 'impact': self.blastRadius *= 0.7
        elif self.bombType == 'landMine': self.blastRadius *= 0.7
        elif self.bombType == 'tnt': self.blastRadius *= 1.45
        elif self.bombType == 'holy': self.blastRadius *= 1.45
        elif self.bombType == 'elonMine': self.blastRadius *= 0.7
        elif self.bombType == 'airstrike': self.blastRadius *= 0.0
        elif self.bombType == 'slipper': self.blastRadius *= 2
        elif self.bombType == 'banana': self.blastRadius *= 0.6
        elif self.bombType == 'shockWave': self.blastRadius *= 0.2
        elif self.bombType == 'petard': self.blastRadius *= 2.5
        elif self.bombType == 'fireBottle': self.blastRadius *= 0.5

        self._explodeCallbacks = []

        # the player this came from
        self.sourcePlayer = sourcePlayer

        # by default our hit type/subtype is our own, but we pick up types of
        # whoever sets us off so we know what caused a chain reaction
        self.hitType = 'explosion'
        self.hitSubType = self.bombType

        # if no owner was provided, use an unconnected node ref
        if owner is None: owner = bs.Node(None)

        # the node this came from
        self.owner = owner

        # adding footing-materials to things can screw up jumping and flying
        # since players carrying those things
        # and thus touching footing objects will think they're on solid ground..
        # perhaps we don't wanna add this even in the tnt case?..
        if self.bombType == 'tnt':
            materials = (factory.bombMaterial,
                         bs.getSharedObject('footingMaterial'),
                         bs.getSharedObject('objectMaterial'))
        else:
            materials = (factory.bombMaterial,
                         bs.getSharedObject('objectMaterial'))

        if self.bombType in ['impact', 'toxic', 'poison',
                             'dirtBomb', 'heal', 'banana',
                             'shockWave', 'portal', 'holy',
                             'airstrike', 'timeBomb', 'fireBottle',
                             'colorBomb']:
            materials = materials + (factory.impactBlastMaterial,)
        elif self.bombType in ['landMine', 'slipper', 'elonMine']:
            materials = materials + (factory.landMineNoExplodeMaterial,)
        elif self.bombType == 'forceBomb':
            materials = materials + (factory.forseBombMaterial,)

        if self.bombType == 'sticky':
            materials = materials + (factory.stickyMaterial,)
        elif not self.notSound:
            materials = materials + (factory.normalSoundMaterial,)

        if self.bombType == 'landMine':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.landMineModel,
                'lightModel': factory.landMineModel,
                'body': 'landMine',
                'shadowSize': 0.44,
                'colorTexture': factory.landMineTex,
                'reflection': 'powerup',
                'reflectionScale': [1.0],
                'materials': materials})

        elif self.bombType == 'elonMine':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.elonMineModel,
                'lightModel': factory.elonMineModel,
                'body': 'landMine',
                'bodyScale': modelSize,
                'shadowSize': 0.44,
                'colorTexture': factory.elonMineTex,
                'reflection': 'powerup',
                'reflectionScale': [1.0],
                'materials': materials})

        elif self.bombType == 'forceBomb':
            self.node = bs.newNode('prop', delegate=self, owner=owner, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.stickyBombModel,
                'lightModel': factory.stickyBombModel,
                'body': 'sphere',
                'bodyScale': modelSize,
                'shadowSize': 0.44,
                'colorTexture': factory.forceTex,
                'reflection': 'powerup',
                'reflectionScale': [1.0],
                'materials': materials})

        elif self.bombType == 'colorBomb':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'body': 'sphere',
                'bodyScale': 0.85,
                'materials': materials})

            self.shield = bs.newNode('shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.5})

            self.shield1 = bs.newNode('shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.43})

            self.shield2 = bs.newNode('shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.36})

            self.node.connectAttr('position', self.shield, 'position')
            self.node.connectAttr('position', self.shield1, 'position')
            self.node.connectAttr('position', self.shield2, 'position')

            bs.animateArray(self.shield2, 'color', 3,
                {0: (0, 0, 10), 100: (10, 0, 0),
                200: (0, 10, 0), 300: (0, 0, 10)},
                True)

            bs.animateArray(self.shield1, 'color', 3,
                {0: (10,0,0), 100: (0, 10, 0),
                200: (0,0,10), 300: (10, 0, 0)},
                True)

            bs.animateArray(self.shield, 'color', 3,
                {0: (0, 10, 0), 100: (0, 0, 10),
                200: (10, 0, 0), 300: (0, 10, 0)},
                True)

            self.shield1 = bs.newNode('shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

            self.node.connectAttr('position', self.shield1, 'position')

            self.shield2 = bs.newNode('shield', owner=self.node, attrs={
                'color': (20, 0, 0),
                'radius': 0.4})

            self.node.connectAttr('position', self.shield2, 'position')

            bs.animate(self.shield2, 'radius',
                {0: 0.1, 300: 0.5, 600: 0.1}, True)

            bs.animateArray(self.shield2, 'color', 3, {
                0: (20, 0, 0), 500: (20.55, 10.65, 0), 1000: (20, 20, 0),
                1500: (0, 10.28, 0), 2000: (0, 20.55, 20.55),
                2500: (0, 0, 20.55),
                3000: (10.48, 0, 20.11), 3500: (20, 0, 0)},
                True)

        elif self.bombType == 'heal':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'body': 'sphere',
                'materials': materials})

            self.shield1 = bs.newNode('shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

            self.node.connectAttr('position', self.shield1, 'position')

            self.shield2 = bs.newNode('shield', owner=self.node, attrs={
                'color': (20, 0, 0),
                'radius': 0.4})

            self.node.connectAttr('position', self.shield2, 'position')

            bs.animate(self.shield2, 'radius',
                {0: 0.1, 300: 0.5, 600: 0.1}, True)

        elif self.bombType == 'portal':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'body': 'sphere',
                'bodyScale': 0.85,
                'materials': materials})

            self.shield1 = bs.newNode('shield', owner=self.node, attrs={
                'color': (1, 1, 1),
                'radius': 0.6})

            self.node.connectAttr('position', self.shield1, 'position')
            
            self.shield2 = bs.newNode('shield', owner=self.node, attrs={
                'color': (0, 0, 20),
                'radius': 0.4})

            self.node.connectAttr('position', self.shield2, 'position')

            bs.animate(self.shield2, 'radius',
                {0: 0.1, 300: 0.5, 600: 0.1}, True)

        elif self.bombType == 'holy':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.holyBombModel,
                'lightModel': factory.holyBombModel,
                'body': 'sphere',
                'bodyScale': modelSize,
                'shadowSize': 0.5,
                'colorTexture': factory.holyTex,
                'reflection': 'powerup',
                'reflectionScale': [3.0],
                'materials': materials})

            bs.playSound(bs.getSound('holyhandhal')) # WOOORMS
            self._trailTimer = bs.Timer(10,
                bs.WeakCall(self._addTrail), repeat=True)

        elif self.bombType == 'airstrike':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'body': 'sphere',
                'materials': materials})
                                          
            self.shield1 = bs.newNode('shield', owner=self.node, attrs={
                'color': (20, 0, 0),
                'radius': 0.6})

            self.node.connectAttr('position', self.shield1, 'position')

        elif self.bombType == 'tnt':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.tntModel,
                'lightModel': factory.tntModel,
                'body': 'crate',
                'shadowSize': 0.5,
                'colorTexture': factory.tntTex,
                'reflection': 'soft',
                'reflectionScale': [0.23],
                'materials': materials})

        elif self.bombType == 'slipper':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.slipperModel,
                'body': 'landMine',
                'bodyScale': modelSize,
                'shadowSize': 0.5,
                'density': 0.7,
                'colorTexture': factory.slipperTex,
                'reflection': 'soft',
                'reflectionScale': [0.4],
                'materials': materials})

        elif self.bombType == 'toxic':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.toxicModel,
                'body': 'capsule',
                'bodyScale': 0.84,
                'shadowSize': 0.5,
                'colorTexture': factory.toxicTex,
                'reflection': 'soft',
                'reflectionScale': [0.4],
                'materials': materials})

        elif self.bombType == 'poison':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.poisonModel,
                'body': 'capsule',
                'bodyScale': modelSize,
                'shadowSize': 0.5,
                'bodyScale': 0.84,
                'colorTexture': factory.poisonTex,
                'reflection': 'soft',
                'reflectionScale': [0.8],
                'materials': materials})

        elif self.bombType == 'fireBottle':
            fuseTime = 7000
            self.node = bs.newNode('bomb', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.fireBottleModel,
                'shadowSize': 0.5,
                'colorTexture': factory.fireBottleTex,
                'reflection': 'soft',
                'reflectionScale': [1],
                'materials': materials})

            if not self.notSound:
                sound = bs.newNode('sound', owner=self.node, attrs={
                    'sound': factory.fuseSound,
                    'volume': 0.25})

                self.node.connectAttr('position', sound, 'position')

            bsUtils.animate(self.node, 'fuseLength',
                {0: 1, fuseTime: 0})

        elif self.bombType == 'dirtBomb':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.dirtModel,
                'body': 'capsule',
                'bodyScale': modelSize+0.4,
                'shadowSize': 0.5,
                'bodyScale': 0.88,
                'density': 0.68,
                'colorTexture': factory.dirtTex,
                'reflection': 'soft',
                'reflectionScale': [0.4],
                'materials': materials})

        elif self.bombType == 'banana':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.bananaModel,
                'body': 'capsule',
                'bodyScale': modelSize+0.4,
                'shadowSize': 0.5,
                'bodyScale': 0.8,
                'density': 1,
                'colorTexture': factory.bananaTex,
                'reflection': 'soft',
                'reflectionScale': [0.4],
                'materials': materials})

        elif self.bombType == 'shockWave':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.shockWaveModel,
                'body': 'capsule',
                'bodyScale': modelSize+0.4,
                'shadowSize': 0.5,
                'bodyScale': 0.9,
                'modelScale': 1.3,
                'colorTexture': factory.shockWaveTex,
                'reflection': 'soft',
                'reflectionScale': [0.7],
                'materials': materials})
            
        elif self.bombType == 'petard':
            fuseTime = 4000
            self.node = bs.newNode('bomb', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.petardModel,
                'shadowSize': 0.3,
                'bodyScale': modelSize,
                'colorTexture': factory.petardTex,
                'reflection': 'soft',
                'reflectionScale': [0.45],
                'materials': materials})

            if not self.notSound:
                sound = bs.newNode('sound', owner=self.node, attrs={
                    'sound': factory.fuseSound,
                    'volume': 0.25})

                self.node.connectAttr('position', sound, 'position')

            bsUtils.animate(self.node ,'fuseLength',
                {0: 1, fuseTime: 0})

        elif self.bombType == 'impact':
            fuseTime = 20000
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'body': 'sphere',
                'model': factory.impactBombModel,
                'shadowSize': 0.3,
                'colorTexture': factory.impactTex,
                'reflection': 'powerup',
                'reflectionScale': [1.5],
                'materials': materials})

            self.armTimer = bs.Timer(200, bs.WeakCall(self.handleMessage,
                                                      ArmMessage()))

            self.warnTimer = bs.Timer(fuseTime-1700,
                                      bs.WeakCall(self.handleMessage,
                                                  WarnMessage()))

        else:
            fuseTime = 3000
            if self.bombType == 'sticky':
                sticky = True
                model = factory.stickyBombModel
                rType = 'sharper'
                rScale = 1.8
            else:
                sticky = False
                model = factory.bombModel
                rType = 'sharper'
                rScale = 1.8

            if self.bombType == 'ice': tex = factory.iceTex
            elif self.bombType == 'sticky': tex = factory.stickyTex
            else: tex = factory.regularTex

            try:
                bm = self.owner is not None \
                    and self.owner.exists() \
                    and self.owner.getDelegate().character == 'Bombman' \
                    and self.bombType == 'normal' \
                    and self.owner.headModel is not None
            except:
                bm = False

            self.node = bs.newNode('bomb', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': bs.getModel('BombmanHead') if bm else model,
                'shadowSize': 0.3,
                'colorTexture': bs.getTexture('BombmanColor') if bm else tex,
                'sticky': sticky,
                'owner': owner,
                'reflection': rType,
                'reflectionScale': [rScale],
                'materials': materials})

            sound = bs.newNode('sound', owner=self.node, attrs={
                'sound': factory.fuseSound,
                'volume': 0.25})

            self.node.connectAttr('position', sound, 'position')
            bsUtils.animate(self.node, 'fuseLength',
                {0: 1.0, fuseTime: 0.0})

        # light the fuse!!!
        if self.bombType not in ('landMine', 'tnt', 'forceBomb',
                                 'toxic', 'poison', 'slipper',
                                 'dirtBomb', 'heal', 'banana',
                                 'shockWave', 'portal', 'holy',
                                 'airstrike', 'elonMine', 'colorBomb'):
            bs.gameTimer(fuseTime,
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))

        bsUtils.animate(self.node, 'modelScale',
            {0: 0, 200: 1.3, 260: 1})

    def getSourcePlayer(self):
        """
        Returns a bs.Player representing the source of this bomb.
        """
        if self.sourcePlayer is None: return bs.Player(None) # empty player ref
        return self.sourcePlayer

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.BombFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        try: return activity._sharedBombFactory
        except Exception:
            f = activity._sharedBombFactory = BombFactory()
            return f

    def onFinalize(self):
        bs.Actor.onFinalize(self)
        # release callbacks/refs so we don't wind up with dependency loops..
        self._explodeCallbacks = []

    def _handleDie(self, m):
        if self.bombType == 'normal':
            try:
                if self.owner is not None \
                        and self.owner.exists() \
                        and self.node is not None \
                        and self.node.exists() \
                        and self.owner.getDelegate().character == 'Bombman' \
                        and self.owner.headModel is None:
                    self.owner.headModel = bs.getModel('BombmanHead')
            except:
                pass

        self.node.delete()

    def _handleOOB(self, m):
        self.handleMessage(bs.DieMessage())

    def _handleImpact(self, m, typeOfBomb):
        node, body = bs.getCollisionInfo('opposingNode', 'opposingBody')
        def go():
            # if we're an impact bomb and we came from this node, don't explode...
            # alternately if we're hitting another impact-bomb from the same source,
            # don't explode...
            try: nodeDelegate = node.getDelegate()
            except Exception: nodeDelegate = None
            if node is not None and node.exists():
                typeOfBombEdit = 'impact' if typeOfBomb == 'landMine' else typeOfBomb
                if (self.bombType == typeOfBombEdit and
                    (node is self.owner
                     or (isinstance(nodeDelegate, Bomb)
                         and nodeDelegate.bombType == typeOfBombEdit
                         and nodeDelegate.owner is self.owner))): return
                else:
                    self.handleMessage(ExplodeMessage())

        if type == 'elonMine': bs.gameTimer(250, go)
        else: go()

    def _handleForceBomb(self, m, node):
        if self.node.exists():
            if node is not None and node is not self.owner \
                    and bs.getSharedObject('playerMaterial') in node.materials:
                self.node.sticky = True
                def on():
                    if self.node is not None and self.node.exists():
                        self.node.extraAcceleration = (0, 80, 0)

                    if self.aim is not None:
                        self.aim.off()

                bs.gameTimer(1, on)

    def _handleDropped(self, m):
        if self.bombType == 'landMine':
            self.armTimer = \
                bs.Timer(1250, bs.WeakCall(self.handleMessage, ArmMessage()))

        elif self.bombType == 'elonMine':
            self.armTimer = \
                bs.Timer(500, bs.WeakCall(self.handleMessage, ArmMessage()))

        elif self.bombType == 'forceBomb':
            self.armTimer = \
                bs.Timer(250, bs.WeakCall(self.handleMessage, ArmMessage()))

        elif self.bombType == 'slipper':
            if not self.slipperThree:
                self.armTimer = \
                    bs.Timer(1250, bs.WeakCall(self.handleMessage, ArmMessage()))

                self.slipperPlanted = True
            else:
                self.slipperThreeDropped = True
                if self.node.exists():
                    def bl():
                        if self.node.exists():
                            bs.Blast(
                                position=self.node.position,
                                blastRadius=0.2).autoRetain()

                    bs.gameTimer(1500, bs.Call(bl))

        # once we've thrown a sticky bomb we can stick to it..
        elif self.bombType == 'sticky':
            def _safeSetAttr(node, attr, value):
                if node.exists(): setattr(node, attr, value)
            bs.gameTimer(
                250, lambda: _safeSetAttr(self.node, 'stickToOwner', True))

    def _handleSplat(self, m):
        node = bs.getCollisionInfo('opposingNode')
        if (node is not self.owner
                and bs.getGameTime()-self._lastStickySoundTime > 1000):
            self._lastStickySoundTime = bs.getGameTime()
            bs.playSound(self.getFactory().stickyImpactSound, 2.0,
                         position=self.node.position)

    def addExplodeCallback(self, call):
        """
        Add a call to be run when the bomb has exploded.
        The bomb and the new blast object are passed as arguments.
        """
        self._explodeCallbacks.append(call)

    def explode(self):
        """
        Blows up the bomb if it has not yet done so.
        """
        if self._exploded: return
        self._exploded = True
        activity = self.getActivity()
        if not self.bombType in ['toxic', 'poison', 'shockWave',
                                 'portal', 'airstrike', 'heal',
                                 'colorBomb']:
            if activity is not None and self.node.exists():
                if self.bombType == 'normal':
                    try:
                        if self.owner is not None \
                                and self.owner.exists() \
                                and self.owner.getDelegate().character == 'Bombman' \
                                and self.owner.headModel is None:
                            self.owner.headModel = bs.getModel('BombmanHead')
                    except:
                        pass

                if self.napalm or self.bombType == 'fireBottle':
                    self.fuseTimer = None
                    bdUtils.Napalm(position=self.node.position)

                blast = Blast(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    blastRadius=self.blastRadius,
                    blastType=self.bombType if not self.notShake else 'turret',
                    sourcePlayer=self.sourcePlayer,
                    hitType=self.hitType,
                    hitSubType=self.hitSubType).autoRetain()

                for c in self._explodeCallbacks: c(self, blast)

                if self.bombType == 'dirtBomb':
                    def slowMo():
                        bs.getSharedObject('globals').slowMotion = \
                            bs.getSharedObject('globals').slowMotion == False

                    slowMo()
                    bs.playSound(bs.getSound('orchestraHitBig2'))
                    bs.gameTimer(600, bs.Call(slowMo))     

        elif self.bombType == 'heal':
            bdUtils.HealBomb(position=self.node.position)
            bs.playSound(self.getFactory().healthBombSound, position=self.node.position)

        elif self.bombType == 'toxic':
            bdUtils.Toxic(position=self.node.position)
            bs.playSound(self.getFactory().toxicSound, position=self.node.position)

        elif self.bombType == 'poison':
            bdUtils.Poison(position=self.node.position)
            bs.playSound(self.getFactory().poisonSound, position=self.node.position)

        elif self.bombType == 'shockWave':
            bdUtils.ShockWave(position=self.node.position)
            bs.playSound(self.getFactory().shockWaveSound, position=self.node.position)

        elif self.bombType == 'portal':
            bdUtils.Portal(
                position1=self.node.position,
                position2=self.owner.position,
                isBomb=True)

        elif self.bombType == 'airstrike':
            bdUtils.Airstrike(position=self.node.position)

        elif self.bombType == 'colorBomb':
            color = (random.uniform(0.1, 2.5),
                     random.uniform(0.1, 2.5),
                     random.uniform(0.1, 2.5))

            bdUtils.ColorBomb(position=self.node.position, color=color)
            scorch = bs.newNode('scorch', attrs={
                'position': self.node.position,
                'size': 2})

            scorch.color = color
            bs.playSound(bs.getSound('paint'), position=self.node.position)
            bsUtils.animate(scorch, 'presence',
                {3000: 1, 26000: 0})

            bs.gameTimer(26000, scorch.delete)

        bs.addStats('Bomb explosions')

        # we blew up so we need to go away
        bs.gameTimer(1, bs.WeakCall(self.handleMessage, bs.DieMessage()))

    def _handleWarn(self, m):
        if self.textureSequence.exists():
            self.textureSequence.rate = 30
            bs.playSound(self.getFactory().warnSound, 0.5,
                         position=self.node.position)

    def _addMaterial(self, material):
        if not self.node.exists(): return
        materials = self.node.materials
        if not material in materials:
            self.node.materials = materials + (material,)

    def _addTrail(self):
        if self.node.exists():
            bs.emitBGDynamics(
                position=self.node.position,
                velocity=(0, 1, 0),
                count=50,
                spread=0.05,
                scale=0.6,
                chunkType='spark')
        else: 
            self._trailTimer = None

    def arm(self):
        """
        Arms land-mines and impact-bombs so
        that they will explode on impact.
        """
        if not self.node.exists(): return
        factory = self.getFactory()
        if self.bombType == 'landMine':
            self.textureSequence = \
                bs.newNode('textureSequence', owner=self.node, attrs={
                    'rate': 30,
                    'inputTextures': (factory.landMineLitTex,
                                      factory.landMineTex)})

            bs.gameTimer(500, self.textureSequence.delete)
            # we now make it explodable.
            bs.gameTimer(250, bs.WeakCall(self._addMaterial,
                                          factory.landMineBlastMaterial))

        elif self.bombType == 'elonMine':
            self.textureSequence = \
                bs.newNode('textureSequence', owner=self.node, attrs={
                    'rate': 30,
                    'inputTextures': (factory.elonMineLitTex,
                                      factory.elonMineTex)})

            bs.gameTimer(500, self.textureSequence.delete)
            bs.playSound(bs.getSound('activateBeep'), position=self.node.position)
            self.aim = bdUtils.AutoAim(self.node, self.owner)
            # we now make it explodable.
            bs.gameTimer(250, bs.WeakCall(self._addMaterial,
                                          factory.landMineBlastMaterial))

        elif self.bombType == 'impact':
            self.textureSequence = \
                bs.newNode('textureSequence', owner=self.node, attrs={
                    'rate': 100,
                    'inputTextures': (factory.impactLitTex,
                                      factory.impactTex,
                                      factory.impactTex)})

            bs.gameTimer(250, bs.WeakCall(self._addMaterial,
                                          factory.landMineBlastMaterial))

        elif self.bombType == 'forceBomb':
            bs.playSound(bs.getSound('activateBeep'), position=self.node.position)
            self.aim = bdUtils.AutoAim(self.node, self.owner)

        elif self.bombType == 'slipper':
            bs.gameTimer(250, bs.WeakCall(self._addMaterial,
                              factory.landMineBlastMaterial))

            bs.playSound(bs.getSound('bombHasBeenPlanted'))

        else:
            raise Exception('arm() should only be called '
                            'on land-mines or impact bombs')

        if not self.bombType in ['forceBomb', 'slipper']:
            self.textureSequence.connectAttr('outputTexture',
                                             self.node, 'colorTexture')

            bs.playSound(factory.activateSound, 0.5, position=self.node.position)

    def rearm(self):
        if not self.node.exists(): return
        factory = self.getFactory()
        if self.bombType == 'slipper':
            self.node.materials = [bs.getSharedObject('objectMaterial')]

        def one():
            bs.playSound(bs.getSound("slipperOne"))

        def two():
            bs.playSound(bs.getSound("slipperTwo"))

        def three():
            bs.playSound(bs.getSound("slipperThree"))

        def blast():
            if self.node.exists():
                if not self.slipperThreeDropped:
                    bs.Blast(
                        position=self.node.position,
                        blastRadius=1).autoRetain()

        def off():
            self.slipperThree = True

        bs.gameTimer(2000, bs.Call(one))
        bs.gameTimer(3500, bs.Call(two))
        bs.gameTimer(5000, bs.Call(three))
        bs.gameTimer(5100, bs.Call(off))
        bs.gameTimer(6600, bs.Call(blast))

    def _handleHit(self, m):
        isPunch = (m.srcNode.exists() and m.srcNode.getNodeType() == 'spaz')

        # normal bombs are triggered by non-punch impacts..
        # impact-bombs by all impacts
        if (not self._exploded and not isPunch
            or self.bombType in ['impact', 'landMine', 'elonMine']):
            # also lets change the owner of the bomb to whoever is setting
            # us off.. (this way points for big chain reactions go to the
            # person causing them)
            if m.sourcePlayer not in [None]:
                self.sourcePlayer = m.sourcePlayer

                # also inherit the hit type (if a landmine sets off by a bomb,
                # the credit should go to the mine)
                # the exception is TNT.  TNT always gets credit.
                if self.bombType != 'tnt':
                    self.hitType = m.hitType
                    self.hitSubType = m.hitSubType

            bs.gameTimer(100+int(random.random()*100),
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))

        self.node.handleMessage(
            "impulse", m.pos[0], m.pos[1], m.pos[2],
            m.velocity[0], m.velocity[1], m.velocity[2],
            m.magnitude, m.velocityMagnitude, m.radius, 0,
            m.velocity[0], m.velocity[1], m.velocity[2])

        if m.srcNode.exists():
            pass

    def handleMessage(self, m):
        if isinstance(m, ExplodeMessage): self.explode()
        elif isinstance(m, SetStickyMessage):
            node = bs.getCollisionInfo('opposingNode')
            self._handleForceBomb(m, node)
        elif isinstance(m, ImpactMessage):
            self._handleImpact(m, typeOfBomb=self.bombType)
        elif isinstance(m, bs.PickedUpMessage):
            # change our source to whoever just picked us up *only* if its None
            # this way we can get points for killing bots with their own bombs
            # hmm would there be a downside to this?...
            if self.bombType == 'slipper':
                if self.slipperPlanted:
                    self.sourcePlayer = m.node.sourcePlayer
                    self.owner = m.node
                    self.rearm()

            elif self.bombType == 'forceBomb' \
                    and self.node.exists() \
                    and self.owner != m.node:
                bs.playSound(
                    bs.getSound('corkPop'),
                    position=self.node.position)

                self.explode()

            elif self.bombType == 'elonMine' \
                    and self.node.exists() \
                    and self.owner != m.node:
                bs.playSound(
                    bs.getSound('corkPop'),
                    position=self.node.position)

                bsUtils.PopupText(
                    bs.Lstr(resource='elonMineDefused'),
                    color=(1, 1, 1),
                    scale=1.0,
                    position=self.node.position).autoRetain()

                self.node.delete()

            if self.sourcePlayer is not None:
                self.sourcePlayer = m.node.sourcePlayer

        elif isinstance(m, SplatMessage): self._handleSplat(m)
        elif isinstance(m, bs.DroppedMessage): self._handleDropped(m)
        elif isinstance(m, bs.HitMessage): self._handleHit(m)
        elif isinstance(m, bs.DieMessage): self._handleDie(m)
        elif isinstance(m, bs.OutOfBoundsMessage): self._handleOOB(m)
        elif isinstance(m, ArmMessage): self.arm()
        elif isinstance(m, WarnMessage): self._handleWarn(m)
        else: bs.Actor.handleMessage(self, m)

class TNTSpawner(object):
    """
    category: Game Flow Classes

    Regenerates TNT at a given point in space every now and then.
    """
    def __init__(self, position, respawnTime=30000):
        """
        Instantiate with a given position and respawnTime (in milliseconds).
        """
        self._position = position
        self._tnt = None
        self._update()
        self._updateTimer = bs.Timer(1000, bs.WeakCall(self._update), repeat=True)
        self._respawnTime = int(random.uniform(0.8, 1.2) * respawnTime)
        self._waitTime = 0

    def _update(self):
        tntAlive = self._tnt is not None and self._tnt.node.exists()
        if not tntAlive:
            # respawn if its been long enough.. otherwise just increment our
            # how-long-since-we-died value
            if self._tnt is None or self._waitTime >= self._respawnTime:
                self._tnt = Bomb(position=self._position, bombType='tnt')
                self._waitTime = 0
            else: self._waitTime += 1000