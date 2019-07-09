import time
import random


site_status = {
    "parked": "True", 
    "timestamp": str(int(time.time()))
}

weather_status = {
    "wind": "blowing", 
    "rain": "no", 
    "timestamp": str(int(time.time()))
}

goto_cmd = {
    "device": "mount_1",
    "ra": random.randint(0,24),
    "dec": random.randint(-90,90),
    "command": "goto",
    "timestamp": str(int(time.time()))
} 

sample_config = {
    "site": "site1",
    "mounts": {
        "mount1": {
            "telescopes": {}
        }, 
        "mount2": {
            "telescopes": {}
        }, 
        "mount3": {
            "telescopes": {}
        },
    }
}

sample_config2 = {
    "site": "site2",
    "mounts": {
        "s2m1": {
            "telescopes": {}
        }, 
    }
}

sample_config3 = {
    "site": "site3",
    "mounts": {
        "s3m1": {
            "telescopes": {
                "s3m1t1": {
                    "cameras": {
                        "cam1": {}
                    }
                }
            }
        }, 
        "s3m2": {
            "telescopes": {
                "s3m2t1": {
                    "cameras": {
                        "cam2": {}
                    }
                }
            }
        }, 
        "s2m3": {
            "telescopes": {
                "s3m3t1":{}
            }
        },
    }
}

sample_config4 = {
    "site": "site4",
    "enclosures": ["enc1", "enc2"],
    "mounts": ["mount1", "mount2", "mount3"],
    "telescopes": ["t1", "t2", "t3", "t4"],
    "cameras": ["cam1", "cam2", "cam3", "cam4", "cam5"], 
    "filters": ["fil1", "fil2", "fil3", "fil4"],
    "flatscreens": ["flt1", "flt2", "flt3"],
    "focusers": ["foc1", "foc2", "foc3", "foc4"],
    "rotators": ["rot1", "rot2", "rot3"],
    "power_cycle_switch": ["pcs1", "pcs2", "pcs3"],
    "weather": ["wx1", "wx2"],
}

sample_config5 = {
    "site": "site5",
    "mounts": {
        "mount1": {
            "telescopes": {
                "t1": {
                    "cameras": {
                        "cam1": {
                            "type": "ccd",
                            "pixels": "2048",
                        },
                        "cam2": {
                            "type": "cmos",
                            "pixels": "8172",
                        },
                    },
                    "focusers": {
                        "foc1": {
                            "cameras": ["cam1", "cam2"]
                        }
                    }
                },
                "t2": {
                    "cameras": {}
                }
            }
            
        },
        "mount2": {
            "telescopes": {
                "t3": {
                    "cameras": {
                        "cam3": {
                            "type": "ccd",
                        }
                    }
                }
            }
        },
    }
}

simple_config = {
    "site": "site4",
    "mount": {
        "mount1": {
            "name": "mount1",
            "driver": 'ASCOM.Simulator.Telescope',
        },
    },
    "camera": {
        "cam1": {
            "name": "cam1",
            "driver": 'ASCOM.Simulator.Camera',
        },
        "cam2": {
            "name": "cam2",
            "driver": 'ASCOM.Simulator.Camera',
        },
    },
    "filter": {
        "fil1": {
            "name": "fil1",
            "driver": "ASCOM.Simulator.Filter",
        }
    },
    "telescope": {
        "telescope1": {
            "name": "telescope1",
            "driver": "ASCOM.Simulator.Telescope"
        }
    }
}

sample_upload_request = {
    "object_name": "raw_data/2019/a_file2.txt"
}