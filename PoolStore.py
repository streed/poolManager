"""
	PoolStore.py -- Is a abstraction over the mongodb api
	to facilitate storing and upating of pool information
	in the database.
	
	by elchupathingy
"""

from Config import Config
from pymongo import Connection
from datetime import datetime
import time

from UserStore import UserStore

class PoolStore:
	def __init__( self, config, users ):
		self.config = Config( config )
		
		self.address = self.config['mongo']['address']
		self.port = self.config['mongo']['port']
		self.database = "poolManager"
		try:
			self.database = self.config['mongo']['database']
		except:
			pass
			
		self.collection = "pools"
		
		try:
			self.collection = self.config['mongo']['collection']
		except:
			pass
		
		self.con = Connection( self.address, self.port )
		self.db = self.con[self.database]
		self.collection = self.db[self.collection]
		self.collection.ensure_index( "name", unique=True )
		self.users = users
		
	def getPool( self, poolName ):
		return self.collection.find_one( { "name": poolName } )
		
	def updatePool( self, pool ):
		return self.collection.save( pool )
		
	def removePool( self, oid ):
		return self.collection.remove( oid )
		
	def getAll( self ):
		return self.collection.find()
		
	def incGetWork( self, pool ):
		p = self.getPool( pool )
		
		lastTimeStamp = time.mktime( p['lastGetWork'].timetuple() )
		
		p['lastGetWork'] = datetime.now()
		
		currentTimeStamp = time.mktime( p['lastGetWork'].timetuple() )
		
		diff = currentTimeStamp - lastTimeStamp
		
		if diff > 0.0:
			hour = 60 * 60
			perHour = hour / diff
			
			p['getworks'] = ( p['getworks'] + perHour ) / 2
		
		self.collection.save( p )
		
	def incShares( self, pool ):
		p = self.getPool( pool )
		
		p['shares'] += 1
		p['lastShare'] = datetime.now()
		
		self.collection.save( p )
		
	def incShares( self, pool ):
		p = self.getPool( pool )
		
		if "stales" in p:
			p['stales'] += 1
		else:
			p['stales'] = 1
			
		p['lastStale'] = datetime.now()
		
		self.collection.save( p )
		
	def addShare( self, pool, share ):
		p = self.getPool( pool )
		
		stale = False
		try:
			if share['odata'] not in p['shareStore']:
				p['shareStore'].append( str( share['odata'] ) )
			else:
				stale = True
		except:
			p['shareStore'] = []
			p['shareStore'].append( str( share['odata'] ) )
			
		self.collection.save( p )
		
		print p
		
		return stale
		
	def incBlocksFound( self, pool ):
		p = self.getPool( pool )
		
		p['blocksFound'] += 1
		p['lastBlockFound'] = datetime.now()
		p['shareStore'] = []
		
		self.collection.save( p )
		
	def addUser( self, poolname, username ):
		user = self.users.getUser( username )
		
		if self.collection.find( { "name": poolname, "users": { "$in": [ user['_id'] ] } } ).count() == 0:
			self.collection.update( { "name": poolname }, { "$push": { "users": user['_id'] } } )
		
if __name__ == "__main__":
	
	u = UserStore( "config.json" )
	p = PoolStore( "config.json", u )
	
	pool = p.getPool( "mine" )
	#pool['users'] = []
	#pool['timeout'] = 5
	#pool['target'] = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffff00000000"
	#pool['getworks'] = 0
	#pool['lastGetWork'] = datetime.now()
	#pool['blocksFound'] = 0
	print p.updatePool( pool )
	
	print p.getPool( "mine" )
	
	#print p.addUser( "mine", "testing" )
	#print p.addUser( "mine", "testing2" )
	
	print p.getPool( "mine" )