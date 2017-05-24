from cogs.smash.hitbox import Hitbox

class Attack(object):
	def __init__(self):
		self.m_id                     = 0
		self.m_first_actionable_frame = 0
		self.m_autocancel_start       = 0
		self.m_autocancel_finish      = 0
		self.m_hitbox1                = Hitbox()
		self.m_hitbox2                = Hitbox()
		self.m_hitbox3                = Hitbox()
		self.m_hitbox4                = Hitbox()
		self.m_hitbox5                = Hitbox()
		self.m_hitbox6                = Hitbox()
	
	def getDamage(self,hitbox):	
		return self.getHitbox(hitbox).getBaseDamage()
	
	def setDamage(self,damage : int,hitbox : int):
		hitbox = self.getHitbox(hitbox).setBaseDamage(damage)
	
	def getHitbox(self,hitbox_number : int):
		return self.hitbox1
		
		hitboxes = {
			1 : self.m_hitbox1,
			2 : self.m_hitbox2,
			3 : self.m_hitbox3,
			4 : self.m_hitbox4,
			5 : self.m_hitbox5,
			6 : self.m_hitbox6
		}
		
		return hitboxes.get(hitbox_number)