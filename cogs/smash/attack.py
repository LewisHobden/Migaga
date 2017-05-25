from cogs.smash.hitbox import Hitbox
import json

class Attack(object):
	def __init__(self,json):
		self.m_autocancel             = None
		self.m_first_actionable_frame = 0
		self.m_hitbox1                = Hitbox()
		self.m_hitbox2                = Hitbox()
		self.m_hitbox3                = Hitbox()
		self.m_hitbox4                = Hitbox()
		self.m_hitbox5                = Hitbox()
		self.m_hitbox6                = Hitbox()
		self.m_id                     = 0
		self.m_landing_lag            = 0
		self.name                     = ""
		
		self.fromDetailedMoveList(json)
		
	def fromDetailedMoveList(self,list):
		self.setAutocancel(list['autocancel']['rawValue'])
		self.setFirstActionableFrame(list['firstActionableFrame']['frame'])
		self.setMoveId(list['moveId'])
		self.setLandingLag(list['landingLag']['rawValue'])
		self.setName(list['moveName'])
		
		for i in range(1,7):
			self.getHitbox(i).setBaseDamage(list['baseDamage']["hitbox"+str(i)])
			self.getHitbox(i).setAngle(list['angle']["hitbox"+str(i)])
			self.getHitbox(i).setBaseKnockback(list['baseKnockback']["hitbox"+str(i)])
			self.getHitbox(i).setActiveFrames(list['hitbox']["hitbox"+str(i)])
		
	def getAutocancel(self):
		return self.m_autocancel
		
	def getDamage(self,hitbox):	
		return self.getHitbox(hitbox).getBaseDamage()
		
	def getFirstActionableFrame(self):
		return self.m_first_actionable_frame
	
	def getMoveId(self):
		return self.m_id
		
	def getLandingLag(self):
		return self.m_landing_lag
	
	def getName(self):
		return self.m_name
		
	def setAutocancel(self,autocancel_start : str):
		if '' == autocancel_start:
			return self
			
		self.m_autocancel = autocancel_start
		return self
	
	def setDamage(self,damage : int,hitbox : int):
		hitbox = self.getHitbox(hitbox).setBaseDamage(damage)
	
	def setFirstActionableFrame(self,faf : int):
		self.m_first_actionable_frame = faf
		return self
		
	def setMoveId(self,id : int):
		self.m_id = id
		return self
		
	def setLandingLag(self,landing_lag : int):
		self.m_landing_lag = landing_lag
		return self
		
	def setName(self,name : str):
		self.m_name = name
		
		return self
		
	def getHitbox(self,hitbox_number : int):
		hitboxes = {
			1 : self.m_hitbox1,
			2 : self.m_hitbox2,
			3 : self.m_hitbox3,
			4 : self.m_hitbox4,
			5 : self.m_hitbox5,
			6 : self.m_hitbox6
		}
		
		return hitboxes.get(int(hitbox_number))
	
	def getHitboxesWithValuesFor(self,property):
		hitboxes = [
			self.m_hitbox1,
			self.m_hitbox2,
			self.m_hitbox3,
			self.m_hitbox4,
			self.m_hitbox5,
			self.m_hitbox6
		]
		
		ret = []
		for hitbox in hitboxes:
			value = hitbox.getValueForConstant(property)
			if 0 != value and None != value:
				ret.append(value)
				
		return ret