#!/home/kels/Documents/projects/netAutomation/pexpect/pexpect/bin/python
from distutils.cmd import Command
from distutils.command.config import config
import json
from xmlrpc.client import Boolean
import pexpect as middleMan

actions=open('./devices.json')
actions=json.load(actions)

#interact with terminal
def interact(child,action):
    if not len(action["expectList"]):
        action["expectList"]=[]

    action["expectList"].extend([middleMan.EOF,middleMan.TIMEOUT])

    if action["query"]:
        print("CLI: %s " %(action["query"]))
        child.sendline(action["query"])
    
    ret=child.expect(action["expectList"])
    # print("before:%s after:%s" %(child.before,child.after))
    return {
        "passed":Boolean(ret not in [len(action["expectList"])-2,len(action["expectList"])-1]),
        "message":child.after if not action["read"] else child.before #child.after[2:len(child.after)-1]
    }


#create terminal child process
def initPexpect(device):
    print('%s %s %s' 
            %(
                (device["access"]or'telnet'),(device["ip"]or'127.0.0.1'),(device["port"]or'23')
            )
        )
    childInstance=middleMan.spawn('%s %s %s' 
            %(
                (device["access"]or'telnet'),(device["ip"]or'127.0.0.1'),(device["port"]or'23')
            )
        )
    expectList=["Router*","router",device["deviceName"]] if device["type"]=="router" else ["switch","switch",device["deviceName"]]
    childInstance.timeout=5
    print("INSTANCE: %s IP: %s MODE: %s PORT:%s" 
        %(
           device["deviceName"],(device["ip"]or'127.0.0.1'),(device["access"]or'telnet'),(device["port"]or'23')
        )
    )
    interact(childInstance,{"expectList":expectList,"query":" ","read":False})
    return childInstance

def generateExpect(device,configProps):
    if Boolean(configProps["read"]):
        return middleMan.EOF
    else:
        return "lool" #work on this later

#generate configs from store
def generateConfigs(deviceConfig,configList,device):
    ret =[]
    if deviceConfig["all"]:
        for command in configList["commands"]:
            ret.append({
                "query":command["base"],
                "expectList":['#',">",device["deviceName"] if not command["expect"] else generateExpect(device,command["expect"])],
                "read":Boolean(command["read"] if command["read"] else False)
            })
    else:
        for param in deviceConfig["params"]:
            command=configList["commands"][param["index"]]
            ret.append({
                "query":command["base"]+(param["value"] or " "),
                "expectList":['#',">",device["deviceName"] if not command["expect"] else generateExpect(device,command["expect"])],
                "read":Boolean(command["read"] if command["read"] else False)
            })     
    return ret

#intry
def iterator():
    #go throw the JSON
    for device in actions['devices']:
        #loop through devices and 
        deviceShell=initPexpect(device)
        for deviceConfigOption in device["configs"]:
            # create config for each device config property
            configs=actions["configs"][deviceConfigOption["index"]]
            genConfigs=generateConfigs(deviceConfigOption,configs,device)
            for config in genConfigs:
                response=interact(deviceShell,config)
                print("PASSED: %s" %(response["passed"]))
            # print(generateConfigs(deviceConfigOption,configs,device))





iterator()