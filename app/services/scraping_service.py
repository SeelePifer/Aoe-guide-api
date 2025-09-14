"""
Optimized service for asynchronous scraping of build data from AoE Companion
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import time
from typing import List, Optional
from app.models.build_models import Build, BuildType, BuildDifficulty
import logging

logger = logging.getLogger(__name__)


class OptimizedScrapingService:
    """Optimized service to extract builds from AoE Companion"""
    
    def __init__(self, max_concurrent_requests: int = 5, timeout: int = 30):
        self.base_url = "https://aoecompanion.com/build-guides"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
    
    async def scrape_builds(self) -> List[Build]:
        """Extract builds from AoE Companion asynchronously"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                
                # Get main page
                builds = await self._scrape_main_page(session)
                
                # Process builds in parallel
                if builds:
                    builds = await self._process_builds_parallel(session, builds)
                
                elapsed_time = time.time() - start_time
                logger.info(f"Scraping completed in {elapsed_time:.2f}s - {len(builds)} builds found")
                
                return builds
                
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []
    
    async def _scrape_main_page(self, session: aiohttp.ClientSession) -> List[Build]:
        """Extract builds from main page"""
        try:
            async with session.get(self.base_url) as response:
                if response.status != 200:
                    logger.error(f"HTTP {response.status} error for {self.base_url}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                builds = []
                
                # Find build sections
                sections = soup.find_all('div', class_=re.compile(r'.*section.*|.*build.*'))
                
                for section in sections:
                    section_builds = await self._extract_builds_from_section(section)
                    builds.extend(section_builds)
                
                return builds
                
        except asyncio.TimeoutError:
            logger.error("Timeout while scraping main page")
            return []
        except Exception as e:
            logger.error(f"Error scraping main page: {e}")
            return []
    
    async def _extract_builds_from_section(self, section) -> List[Build]:
        """Extract builds from specific section"""
        builds = []
        
        # Find section title to determine type
        section_title = section.find(['h2', 'h3', 'h4'])
        if not section_title:
            return builds
            
        title_text = section_title.get_text().strip().lower()
        build_type = self._determine_build_type(title_text)
        
        if not build_type:
            return builds
        
        # Find builds within section
        build_items = section.find_all(['div', 'article'], class_=re.compile(r'.*build.*|.*card.*|.*item.*'))
        
        for item in build_items:
            build = self._extract_build_from_item(item, build_type)
            if build:
                builds.append(build)
        
        return builds
    
    async def _process_builds_parallel(self, session: aiohttp.ClientSession, builds: List[Build]) -> List[Build]:
        """Process builds in parallel to get additional details"""
        tasks = []
        
        for build in builds:
            task = self._enhance_build_data(session, build)
            tasks.append(task)
        
        # Process in batches to avoid overloading server
        enhanced_builds = []
        for i in range(0, len(tasks), self.max_concurrent_requests):
            batch = tasks[i:i + self.max_concurrent_requests]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Build):
                    enhanced_builds.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Error enhancing build: {result}")
        
        return enhanced_builds
    
    async def _enhance_build_data(self, session: aiohttp.ClientSession, build: Build) -> Build:
        """Enhance build data with additional information"""
        async with self.semaphore:  # Limit concurrency
            try:
                # Here you could make additional requests to get more details
                # For now, just return the original build
                await asyncio.sleep(0.1)  # Simulate processing
                return build
            except Exception as e:
                logger.warning(f"Error enhancing build {build.name}: {e}")
                return build
    
    def _determine_build_type(self, title_text: str) -> Optional[BuildType]:
        """Determine build type based on section title"""
        if 'feudal rush' in title_text:
            return BuildType.FEUDAL_RUSH
        elif 'fast castle' in title_text:
            return BuildType.FAST_CASTLE
        elif 'dark age rush' in title_text or 'drush' in title_text:
            return BuildType.DARK_AGE_RUSH
        elif 'water' in title_text:
            return BuildType.WATER_MAPS
        return None
    
    def _extract_build_from_item(self, item, build_type: BuildType) -> Optional[Build]:
        """Extract build information from HTML element"""
        # Extract build name
        name_elem = item.find(['h3', 'h4', 'h5', 'strong', 'b'])
        if not name_elem:
            return None
            
        name = name_elem.get_text().strip()
        
        # Extract description
        desc_elem = item.find('p') or item.find('div', class_=re.compile(r'.*desc.*'))
        description = desc_elem.get_text().strip() if desc_elem else ""
        
        # Determine difficulty
        difficulty = self._determine_difficulty(description, name)
        
        # Extract age times
        feudal_time, castle_time, imperial_time = self._extract_age_times(description)
        
        return Build(
            name=name,
            difficulty=difficulty,
            description=description,
            build_type=build_type,
            feudal_age_time=feudal_time,
            castle_age_time=castle_time,
            imperial_age_time=imperial_time
        )
    
    def _determine_difficulty(self, description: str, name: str) -> BuildDifficulty:
        """Determine build difficulty"""
        text_lower = (description + " " + name).lower()
        
        if 'beginner' in text_lower:
            return BuildDifficulty.BEGINNER
        elif 'advanced' in text_lower:
            return BuildDifficulty.ADVANCED
        else:
            return BuildDifficulty.INTERMEDIATE
    
    def _extract_age_times(self, description: str) -> tuple:
        """Extract times for different ages"""
        feudal_time = None
        castle_time = None
        imperial_time = None
        
        # Search for time patterns
        feudal_patterns = re.findall(r'Feudal Age (\d+)', description)
        if feudal_patterns:
            feudal_time = int(feudal_patterns[0])
        
        castle_patterns = re.findall(r'Castle Age (\d+)', description)
        if castle_patterns:
            castle_time = int(castle_patterns[0])
        
        imperial_patterns = re.findall(r'Imperial Age (\d+)', description)
        if imperial_patterns:
            imperial_time = int(imperial_patterns[0])
        
        return feudal_time, castle_time, imperial_time


# Alias for backward compatibility
ScrapingService = OptimizedScrapingService