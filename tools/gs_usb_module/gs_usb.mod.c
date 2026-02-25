#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x25f8bfc1, "module_layout" },
	{ 0x1bd17b3e, "can_change_mtu" },
	{ 0xd81a27d7, "usb_deregister" },
	{ 0x83f07a09, "usb_register_driver" },
	{ 0x4ec5ffc, "can_free_echo_skb" },
	{ 0x5ae5183, "consume_skb" },
	{ 0x34d278b1, "can_put_echo_skb" },
	{ 0x4829a47e, "memcpy" },
	{ 0xf83251ef, "kfree_skb_reason" },
	{ 0x15e326ad, "alloc_can_skb" },
	{ 0xac14fe76, "netif_rx" },
	{ 0x11c3e6d6, "alloc_can_err_skb" },
	{ 0x34a0c653, "netif_tx_wake_queue" },
	{ 0x5d76950f, "can_get_echo_skb" },
	{ 0xd35cce70, "_raw_spin_unlock_irqrestore" },
	{ 0x34db050b, "_raw_spin_lock_irqsave" },
	{ 0x3ea1b6e4, "__stack_chk_fail" },
	{ 0xf0644ef8, "usb_unanchor_urb" },
	{ 0x57a14207, "netdev_err" },
	{ 0x8c676699, "netif_device_detach" },
	{ 0x7504e97d, "usb_alloc_urb" },
	{ 0x865f28c0, "usb_free_urb" },
	{ 0x46834faf, "usb_submit_urb" },
	{ 0x802f71a3, "usb_anchor_urb" },
	{ 0xa72c0785, "usb_alloc_coherent" },
	{ 0xb838aa76, "open_candev" },
	{ 0xb30d7132, "netdev_warn" },
	{ 0x755830df, "close_candev" },
	{ 0x69f38847, "cpu_hwcap_keys" },
	{ 0x14b89635, "arm64_const_caps_ready" },
	{ 0xc5feb598, "register_candev" },
	{ 0xf07bb259, "alloc_candev_mqs" },
	{ 0x77d24c69, "free_candev" },
	{ 0x962c8ae1, "usb_kill_anchored_urbs" },
	{ 0x4bac6cd1, "unregister_candev" },
	{ 0x85fd2dbe, "_dev_info" },
	{ 0x745fbadf, "netdev_info" },
	{ 0x8abcf63a, "usb_free_coherent" },
	{ 0xd9a5ea54, "__init_waitqueue_head" },
	{ 0xdcb764ad, "memset" },
	{ 0x89c9a638, "_dev_err" },
	{ 0x37a0cba, "kfree" },
	{ 0x27a2116c, "usb_control_msg" },
	{ 0xd58d4b67, "kmem_cache_alloc_trace" },
	{ 0xc1c7e6c0, "kmalloc_caches" },
	{ 0x1fdc7df2, "_mcount" },
};

MODULE_INFO(depends, "can-dev");

MODULE_ALIAS("usb:v1D50p606Fd*dc*dsc*dp*ic*isc*ip*in00*");
MODULE_ALIAS("usb:v1209p2323d*dc*dsc*dp*ic*isc*ip*in00*");
