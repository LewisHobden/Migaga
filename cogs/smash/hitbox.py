class Hitbox(object):
	BASE_DAMAGE      = 1
	BASE_KNOCKBACK   = 2
	KNOCKBACK_GROWTH = 3
	ANGLE            = 4
	
	def __init__(self):
		self.m_base_damage      = 0
		self.m_base_knockback   = 0
		self.m_knockback_growth = 0
		self.m_angle            = 0
		self.m_active_frames    = ""
	
	def getAngle(self):
		return self.m_angle
	
	def getBaseDamage(self):
		return self.m_base_damage
		
	def getBaseKnockback(self):
		return self.m_base_knockback
	
	def getKnockbackGrowth(self):
		return self.m_knockback_growth
		
	def setAngle(self,angle : int):
		self.m_angle = angle
		return self
		
	def setActiveFrames(self,active_frames):
		self.m_active_frames = active_frames
		return self
		
	def getActiveFrames(self):
		return self.m_active_frames
	
	def setBaseDamage(self,damage : int):
		self.m_base_damage = damage
		return self
		
	def setBaseKnockback(self,knockback : int):
		self.m_base_knockback = knockback
		return self
	
	def setKnockbackGrowth(self,knockback_growth : int):
		self.m_knockback_growth = knockback_growth
		return self
		
	def hasData(self):
		if self.m_base_damage != 0 and self.m_base_damage != "":
			return True
		elif self.m_base_damage != 0 and self.m_base_damage != "":
			return True
		elif self.m_knockback_growth != 0 and self.m_knockback_growth != "":
			return True
		elif self.m_angle != 0 and self.m_angle != "":
			return True
		elif self.m_active_frames != 0 and self.m_active_frames != "":
			return True
			
		return False
		
	def getValueForConstant(self,constant):
		constant = int(constant)
		if constant == BASE_DAMAGE:
			return self.getBaseDamage()
		elif constant == BASE_KNOCKBACK:
			return self.getBaseKnockback()
		elif constant == KNOCKBACK_GROWTH:
			return self.getKnockbackGrowth()
		elif constant == ANGLE:
			return self.getAngle()