

class FrozenMeta(type):
    def __setattr__(cls, name, value):
        # 攔截對類別屬性的賦值行為
        raise AttributeError(f"無法修改常數屬性: '{name}'")