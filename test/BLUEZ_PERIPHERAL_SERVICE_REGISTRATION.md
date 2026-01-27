# BlueZ Peripheral - GATT Service Registration Analysis

## Overview
This document details how the `bluez_peripheral` library manages GATT service registration with BlueZ through D-Bus.

---

## 1. Service.register() Internal Workflow

### Method Signature
```python
async def register(
    self,
    bus: MessageBus,
    *,
    path: Optional[str] = None,
    adapter: Optional[Adapter] = None,
) -> None:
```

### Internal Process
When `Service.register()` is called, it performs the following steps:

1. **Creates a ServiceCollection wrapper** (Line: service.py)
   ```python
   collection = ServiceCollection([self])
   ```
   - A single Service is wrapped in a ServiceCollection to manage it as a group
   - ServiceCollection is the actual handler for BlueZ GattManager registration

2. **Delegates registration to ServiceCollection**
   ```python
   await collection.register(bus, path=path, adapter=adapter)
   self._collection = collection
   ```
   - The Service stores reference to its collection for later unregistration
   - Stores internal state: `self._collection`

### ServiceCollection.register() Details
The ServiceCollection handles the actual GattManager interaction:

```python
async def register(
    self,
    bus: MessageBus,
    *,
    path: Optional[str] = None,
    adapter: Optional[Adapter] = None,
) -> None:
    # Step 1: Get the adapter (use first adapter if not specified)
    self._adapter = await Adapter.get_first(bus) if adapter is None else adapter
    
    # Step 2: Export the service hierarchy on D-Bus
    self.export(bus, path=path)
    
    # Step 3: Get GattManager1 interface from the adapter
    manager = self._adapter.get_gatt_manager()
    
    # Step 4: Call RegisterApplication on org.bluez.GattManager1
    async with bluez_error_wrapper():
        await manager.call_register_application(self.export_path, {})
```

---

## 2. Automatic GattManager Registration

### YES - Automatic Registration Occurs

**The answer is: YES, `Service.register()` automatically calls `RegisterApplication` on `org.bluez.GattManager1`.**

### Detailed Flow:
1. When you call `await service.register(bus, path="/me/wehrfritz/bluez_peripheral/service_hid")`, the library:
   - Wraps the service in a `ServiceCollection`
   - Exports it on D-Bus at the specified path
   - **Automatically invokes**: `GattManager1.RegisterApplication(path, {})`

2. The call happens in `ServiceCollection.register()`:
   ```python
   manager = self._adapter.get_gatt_manager()
   async with bluez_error_wrapper():
       await manager.call_register_application(self.export_path, {})
   ```

3. This is done **WITHOUT requiring manual intervention** from the user

### Evidence from Your Code:
In [BleKeyboard.py](BleKeyboard.py#L60-L62):
```python
await self.battery_service.register(self.bus, path="/me/wehrfritz/bluez_peripheral/service_battery")
await self.device_info_service.register(self.bus, path="/me/wehrfritz/bluez_peripheral/service_info")
await self.hid_service.register(self.bus, path="/me/wehrfritz/bluez_peripheral/service_hid")
```

You don't call `GattManager.RegisterApplication()` explicitly—`bluez_peripheral` handles it internally.

---

## 3. Path Structure Requirements for Discoverability

### Required Path Format
GATT services must be exported on D-Bus with a valid hierarchical path structure:

#### Valid Path Examples:
```
/me/wehrfritz/bluez_peripheral/service_battery
/me/wehrfritz/bluez_peripheral/service_info
/me/wehrfritz/bluez_peripheral/service_hid
/me/wehrfritz/equilibrium/remote/service_battery
/me/wehrfritz/equilibrium/remote/service_hid
/com/spacecheese/bluez_peripheral/service_collection/service0
```

#### Path Structure Rules:
1. **Absolute path required**: Must start with `/`
2. **Hierarchical structure**: Forward-slash separated components
3. **Unique per service**: Each service needs a unique path
4. **Application root**: Services must be children of an application root path

#### Default Path if Not Specified:
If no `path` parameter is provided, ServiceCollection uses:
```python
_DEFAULT_PATH_PREFIX = "/com/spacecheese/bluez_peripheral/service_collection"
```

When exported as children, they become:
```
/com/spacecheese/bluez_peripheral/service_collection/service0
/com/spacecheese/bluez_peripheral/service_collection/service1
/com/spacecheese/bluez_peripheral/service_collection/service2
```

### Path Generation for Child Services
The `HierarchicalServiceInterface.export()` method generates paths for characteristics and descriptors:

```python
def export(self, bus: MessageBus, *, num: Optional[int] = 0, path: Optional[str] = None) -> None:
    if path is None:
        if self._parent is not None:
            # Auto-generate path: {parent_path}/{service._BUS_PREFIX}{num}
            path = f"{self._parent.export_path}/{self._BUS_PREFIX}{num}"
```

#### Characteristic Paths Example:
If service is at: `/me/wehrfritz/bluez_peripheral/service_hid`
- Characteristics are auto-numbered: `characteristic0`, `characteristic1`, etc.
- Full paths become:
  ```
  /me/wehrfritz/bluez_peripheral/service_hid/characteristic0
  /me/wehrfritz/bluez_peripheral/service_hid/characteristic1
  /me/wehrfritz/bluez_peripheral/service_hid/characteristic2
  ```

### Class Reference for Path Prefixes:
```python
class Service(HierarchicalServiceInterface):
    _BUS_PREFIX = "service"  # Auto-prepended when num is provided

class characteristic(HierarchicalServiceInterface):
    _BUS_PREFIX = "char"  # Auto-prepended for characteristics

class descriptor(HierarchicalServiceInterface):
    _BUS_PREFIX = "desc"  # Auto-prepended for descriptors
```

### Why Paths Matter for Discoverability:
- **D-Bus Object Paths**: BlueZ uses D-Bus object paths to identify GATT objects
- **GattManager1.RegisterApplication()**: Requires a valid D-Bus path as the application root
- **Path Validation**: BlueZ validates that registered services exist at the specified paths on D-Bus
- **Hierarchical Relationship**: Parent-child paths define the GATT hierarchy (Service → Characteristic → Descriptor)

---

## 4. Multiple Services Sharing an Application Root Path

### How It Works

Multiple services **do NOT directly share a single path**—instead they share a **common application root path** via `ServiceCollection`.

#### Method 1: Separate Service.register() Calls (Your Current Implementation)
```python
# Each service creates its own ServiceCollection wrapper
await service1.register(bus, path="/app/service1")
await service2.register(bus, path="/app/service2")
await service3.register(bus, path="/app/service3")
```

**Behavior:**
- Each `Service.register()` creates a new `ServiceCollection`
- Each ServiceCollection calls `RegisterApplication()` separately
- Each service registers independently with BlueZ

**Drawback:** Multiple D-Bus RegisterApplication calls

**Your Code Example** ([HidRemoteProfile.py](BluetoothManager/profiles/HidRemoteProfile.py#L47-L60)):
```python
await self.battery_service.register(
    bus, 
    path="/me/wehrfritz/equilibrium/remote/service_battery"
)
await self.device_info_service.register(
    bus, 
    path="/me/wehrfritz/equilibrium/remote/service_info"
)
await self.hid_service.register(
    bus, 
    path="/me/wehrfritz/equilibrium/remote/service_hid"
)
```

#### Method 2: Single ServiceCollection for Multiple Services (Recommended)
```python
from bluez_peripheral.gatt.service import ServiceCollection

# Create a single collection with multiple services
services = [service1, service2, service3]
collection = ServiceCollection(services)

# Single RegisterApplication call for all services
await collection.register(bus, path="/app/root")
```

**Behavior:**
- Single ServiceCollection manages all services
- Single `RegisterApplication()` call to BlueZ
- All services share the same application root
- Services become children of the root path:
  ```
  /app/root/service0  (service1)
  /app/root/service1  (service2)
  /app/root/service2  (service3)
  ```

**Advantages:**
- More efficient (single D-Bus call)
- Clearer hierarchy
- Atomic registration/unregistration

### Path Hierarchy Under Shared Root

If you use a shared ServiceCollection:
```
/app/root                           # Application root
├── /app/root/service0              # Service 1 (Battery Service)
│   ├── /app/root/service0/char0    # Characteristic 1
│   └── /app/root/service0/char1    # Characteristic 2
├── /app/root/service1              # Service 2 (Device Info Service)
│   ├── /app/root/service1/char0    # Characteristic 1
│   └── /app/root/service1/char1    # Characteristic 2
└── /app/root/service2              # Service 3 (HID Service)
    ├── /app/root/service2/char0    # Characteristic 1
    └── /app/root/service2/char1    # Characteristic 2
```

### Multiple RegisterApplication Calls (Your Current Approach)

Your implementation registers each service independently:

```
/me/wehrfritz/equilibrium/remote/service_battery/    (RegisterApplication call)
├── characteristic0
└── characteristic1

/me/wehrfritz/equilibrium/remote/service_info/       (RegisterApplication call)
├── characteristic0
└── characteristic1

/me/wehrfritz/equilibrium/remote/service_hid/        (RegisterApplication call)
├── characteristic0
└── characteristic1
```

**This is valid but less efficient** because each service triggers a separate `RegisterApplication()` D-Bus call.

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Service.register() Wrapper** | Creates internal `ServiceCollection([self])` |
| **Automatic GattManager Call** | ✅ YES - `RegisterApplication()` called automatically |
| **Interface Used** | `org.bluez.GattManager1` on the Bluetooth adapter |
| **Path Required** | ✅ YES - Absolute D-Bus path required for each service |
| **Path Format** | `/component/hierarchy/service_name` format |
| **Auto-generated Child Paths** | `{parent_path}/service0`, `{parent_path}/char0`, `{parent_path}/desc0` |
| **Default Path Prefix** | `/com/spacecheese/bluez_peripheral/service_collection` |
| **Multiple Services** | Can register separately (current approach) or in shared ServiceCollection |
| **Shared Root Method** | Create single `ServiceCollection([service1, service2, service3])` and register once |
| **Current Implementation** | Each service registered independently with separate paths |

---

## Code Flow Diagram

```
User Code
├── service.register(bus, path="/custom/path")
│   └── Internal: ServiceCollection([service])
│       ├── export(bus, path="/custom/path")
│       │   └── D-Bus Export
│       │       ├── Service at /custom/path
│       │       ├── Characteristics at /custom/path/char0, char1, ...
│       │       └── Descriptors at /custom/path/charN/desc0, desc1, ...
│       │
│       └── manager.call_register_application("/custom/path", {})
│           └── org.bluez.GattManager1.RegisterApplication()
│               └── BlueZ discovers services on D-Bus
│
└── Eventually: service.unregister()
    └── Internal: collection.unregister()
        ├── manager.call_unregister_application()
        └── unexport() from D-Bus
```

