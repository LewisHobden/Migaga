class Hitbox(object):
	def __init__(self):
		self.m_base_damage      = 0
		self.m_base_knockback   = 0
		self.m_knockback_growth = 0
		self.m_angle            = 0
	
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
	
	def setBaseDamage(self,damage : int):
		self.m_base_damage = damage
		return self
		
	def setBaseKnockback(self,knockback : int):
		self.m_base_knockback = knockback
		return self
	
	def setKnockbackGrowth(self,knockback_growth : int):
		self.m_knockback_growth = knockback_growth
		return self