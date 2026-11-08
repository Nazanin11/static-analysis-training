# Graph Report - bird-2.17 (2).1  (2026-11-03)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 5541 nodes · 15840 edges · 228 communities (204 shown, 24 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 4341 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- net.h
- ospf_is_v2
- topology.c
- bgp/packets.c
- attrs.c
- ip.h
- proto.c
- bgp_config
- bird.h
- rpki.c
- flowspec.c
- tm_start
- lsalib.c
- babel.c
- sock
- main.c
- net_addr
- bfd.c
- rt-attr.c
- client.c
- ip_addr
- cf_error
- mpls.c
- stdlib
- babel/packets.c
- ospf_receive_lsupd
- unix/io.c
- tm_stop
- bsd-netlink/netlink.c
- linux/netlink.c
- resource
- bgp_proto
- radv.c
- trie_test.c
- mac_test.c
- current_time
- config
- channel
- ospf/iface.c
- bgp.h
- rt-table.c
- init_list
- rte
- mrt.c
- bmp.c
- ospf.c
- birdtest.c
- rtable
- add_tail
- rip.c
- bgp.c
- rt-fib.c
- ospf/neighbor.c
- slist_test.c
- rip/packets.c
- proto_configure_channel
- proto
- mb_free
- krt.c
- rta
- nest/iface.c
- bgp_parse_state
- rte_update2
- bgp_channel
- bt_init
- ev_schedule
- l3vpn.c
- hash.h
- krt-sock.c
- a-set.c
- bgp_conn
- log.c
- bgp_channel_config
- nest/neighbor.c
- bfd/io.c
- bmp_proto
- die
- nl_send_route
- bitmap.c
- ip_test.c
- ospf_rx_hook
- lp_alloc_adata
- BIRDPrinter
- mac.c
- proto-hooks.c
- rfree
- a-path.c
- proto_config
- u32
- bmp_route_monitor_notify
- birdcl.c
- sym_scope
- ipa_equal
- blake2s.c
- perf.c
- static.c
- channel_config
- attrs.h
- tree_test.c
- vpn_rd
- blake2b_state
- cli.c
- proto_stats
- protocol_class
- ea_get_int
- cmds.c
- blake2b.c
- uint_cmp
- nl_parse_route
- rte
- bgp_caps
- tcp_ao_getsockopt_ext
- val_compare
- if
- checksum.c
- hash_test.c
- printf.c
- a-set_test.c
- proto_build
- benchmark_fib_dataset
- bgp_af_caps
- bmap_test
- lists_test.c
- tcp_ao_del_ext
- tcp_ao_info_opt_ext
- tcp_ao_add_ext
- unaligned.h
- .gitlab-ci.yml
- IMG_NAME
- lp_alloc
- protocol
- bfd/packets.c
- changes
- blake2b_param
- blake2s_param
- ospf3_get_prefix
- bsd/krt-sys.h
- buffer
- mpls_fec_map
- bitops_test.c
- blake2.h
- mpls_domain
- bmp_config
- rt_show_net
- blake2-impl.h
- current_real_time
- uint
- bitops.h
- heap_test.c
- md5.c
- mpls_fec
- babel_handle_seqno_request
- include_file_stack
- linux/netlink-sys.h
- mpls_range_config
- mpls_range
- current_time_now
- variables
- setkey.h
- sha1.c
- sl_free
- mpls_domain_config
- bmp_stream
- log_open_udp
- tag-collect
- docker-centos-8-amd64
- docker-debian-10-amd64
- docker-debian-10-i386
- docker-debian-11-amd64
- docker-docbuilder
- docker-fedora-32-amd64
- docker-fedora-33-amd64
- docker-fedora-34-amd64
- docker-fedora-35-amd64
- docker-fedora-36-amd64
- docker-fedora-37-amd64
- docker-fedora-38-amd64
- docker-fedora-39-amd64
- docker-fedora-40-amd64
- docker-fedora-41-amd64
- docker-fedora-42-amd64
- docker-opensuse-15.0-amd64
- docker-opensuse-15.1-amd64
- docker-opensuse-15.3-amd64
- docker-opensuse-15.4-amd64
- docker-opensuse-15.5-amd64
- docker-ubuntu-18.04-amd64
- main
- lp_state
- strtoul.c
- as_path_prepend
- ea_set_attr
- tcp-ao.h
- kif_force_scan
- blake2b_constant
- blake2s_constant
- bmp_table
- krt_scan_timer_kick
- test-bird.sh
- mpls_handle
- bmp_peer
- monitoring_rib
- random_bytes
- resclass
- resmem
- proto_spec
- krt_get_attr

## God Nodes (most connected - your core abstractions)
1. `sock` - 168 edges
2. `ip_addr` - 140 edges
3. `current_time()` - 111 edges
4. `add_tail()` - 87 edges
5. `bgp_config` - 84 edges
6. `init_list()` - 73 edges
7. `ea_list` - 67 edges
8. `rem_node()` - 67 edges
9. `rtable` - 64 edges
10. `ip6_addr` - 62 edges

## Surprising Connections (you probably didn't know these)
- `mpls_compare_range_configs()` --calls--> `uint_cmp()`  [INFERRED]
  nest/mpls.c → lib/birdlib.h
- `aggregator_start()` --calls--> `sl_new()`  [INFERRED]
  proto/aggregator/aggregator.c → lib/slab.c
- `aggregator_build()` --calls--> `proto_build()`  [INFERRED]
  proto/aggregator/aggregator.c → nest/proto.c
- `babel_read_router_id()` --calls--> `get_u64()`  [INFERRED]
  proto/babel/packets.c → lib/unaligned.h
- `config_do_commit()` --calls--> `filter_commit()`  [INFERRED]
  conf/conf.c → filter/filter.c

## Import Cycles
- None detected.

## Communities (228 total, 24 thin omitted)

### Community 0 - "net.h"
Cohesion: 0.04
Nodes (81): ip4_zero(), ip6_zero(), rd_zero(), ipa_in_net_ip4(), ipa_in_net_ip6(), ipa_in_px4(), ipa_in_px6(), net_compare_aspa() (+73 more)

### Community 1 - "ospf_is_v2"
Cohesion: 0.07
Nodes (79): u32_masklen(), ipa_from_u32(), nexthop_merge(), ospf_iface_find(), lsa_parse_ext(), lsa_parse_sum_rt(), lsa_walk_rt_init(), find_neigh() (+71 more)

### Community 2 - "topology.c"
Cohesion: 0.07
Nodes (73): u32_mkmask(), ospf_is_ip4(), ospf_is_ip6(), add_link_lsa(), add_prefix(), add_rt2_lsa_link(), add_rt3_lsa_link(), bcast_net_active() (+65 more)

### Community 3 - "bgp/packets.c"
Cohesion: 0.08
Nodes (74): put_ip4(), put_rd(), lp_restore(), lp_save(), get_u16(), get_u8(), put_u16(), put_u32() (+66 more)

### Community 4 - "attrs.c"
Cohesion: 0.09
Nodes (75): bsprintf(), ea_list, ea_unset_attr(), ea_do_prune(), ea_do_sort(), ea_merge(), ea_scan(), ea_sort() (+67 more)

### Community 5 - "ip.h"
Cohesion: 0.06
Nodes (68): trie_match_next_longest_ip4(), trie_match_next_longest_ip6(), attach_node(), attach_node4(), attach_node6(), f_new_trie(), new_node(), new_node4() (+60 more)

### Community 6 - "proto.c"
Cohesion: 0.05
Nodes (73): filter_name(), filter_same(), channel_copy_config(), channel_do_flush(), channel_do_start(), channel_do_up(), channel_feed_loop(), channel_graceful_restart_unlock() (+65 more)

### Community 7 - "bgp_config"
Cohesion: 0.03
Nodes (79): bgp_config, allow_as_sets, allow_local_as, allow_local_pref, allow_med, ao_keys, auth_type, bfd (+71 more)

### Community 8 - "bird.h"
Cohesion: 0.07
Nodes (19): cli_config, linpool, f_cache_eattrs(), f_rta_cow(), f_rte_cow(), filter_commit(), dump_request, linpool (+11 more)

### Community 9 - "rpki.c"
Cohesion: 0.06
Nodes (62): tm_format_real_time(), tm_format_time(), get_u32he(), put_u32he(), rpki_check_interval(), rpki_check_receive_packet(), rpki_connected_hook(), rpki_err_hook() (+54 more)

### Community 10 - "flowspec.c"
Cohesion: 0.08
Nodes (65): builder_add_finish(), builder_add_prepare(), builder_write_parts(), flow4_first_part(), flow4_get_part(), flow4_net_format(), flow4_next_part(), flow4_validate() (+57 more)

### Community 11 - "tm_start"
Cohesion: 0.06
Nodes (59): cli_parse(), config_init(), ca_lookup(), ev_new(), ev_new_init(), idm_init(), lp_new(), mb_alloc() (+51 more)

### Community 12 - "lsalib.c"
Cohesion: 0.06
Nodes (50): fletcher16_compute(), fletcher16_final(), fletcher16_init(), fletcher16_update(), fletcher16_update_n32(), straightforward_fletcher16_checksum(), straightforward_fletcher16_compute(), t_fletcher16_checksum() (+42 more)

### Community 13 - "babel.c"
Cohesion: 0.07
Nodes (61): net_copy(), sl_allocz(), babel_add_seqno_request(), babel_auth_check_pc(), babel_auth_reset_index(), babel_auth_send_challenge_reply(), babel_auth_send_challenge_request(), babel_build_ihu() (+53 more)

### Community 14 - "sock"
Cohesion: 0.06
Nodes (61): bstrbintohex(), toxdigit(), bgp_listen_sock_err(), sock, rpki_fire_tx(), rpki_tx_hook(), sk_set_md5_in_sasp_db(), sk_add_ao_key() (+53 more)

### Community 15 - "main.c"
Cohesion: 0.06
Nodes (50): cf_symbol_is_local(), config_commit(), config_confirm(), config_do_commit(), config_done(), config_free(), config_free_old(), config_status() (+42 more)

### Community 16 - "net_addr"
Cohesion: 0.08
Nodes (52): t_trie_walk(), trie_add_prefix(), trie_match_net(), trie_walk_next(), ip4_and(), ip4_classify(), ip4_mkmask(), ip6_and() (+44 more)

### Community 17 - "bfd.c"
Cohesion: 0.08
Nodes (53): bfd_add_request(), bfd_add_session(), bfd_auth_name(), bfd_copy_config(), bfd_diag_name(), bfd_drop_requests(), bfd_find_iface_config(), bfd_find_session_by_addr() (+45 more)

### Community 18 - "rt-attr.c"
Cohesion: 0.06
Nodes (48): ea_custom_name(), krt_sys_get_attr(), cli_printf(), cli_separator(), proto_iterate_named(), nexthop_equal(), nexthop_same(), rt_unlock_hostentry() (+40 more)

### Community 19 - "client.c"
Cohesion: 0.06
Nodes (40): add_history_dedup(), cleanup(), history_init(), input_complete(), input_got_line(), input_help(), input_hide(), input_init() (+32 more)

### Community 20 - "ip_addr"
Cohesion: 0.07
Nodes (46): trie_add_node(), trie_amask_to_local(), ip4_ntop(), ip4_px_ntop(), ip6_ntop(), ip_addr, ip_ntop(), ip_ntox() (+38 more)

### Community 21 - "cf_error"
Cohesion: 0.06
Nodes (36): cf_error(), cfg_strdup(), bs_same(), f_type_element_type(), f_type_name(), pm_same(), pmi_same(), val_same() (+28 more)

### Community 22 - "mpls.c"
Cohesion: 0.08
Nodes (44): config_add_obstacle(), lmap_test(), mpls_apply_fec(), mpls_channel_cleanup(), mpls_channel_reconfigure(), mpls_channel_start(), mpls_compare_range_configs(), mpls_damage_fec() (+36 more)

### Community 23 - "stdlib"
Cohesion: 0.05
Nodes (21): bt_assert_filter(), t_reconfig(), test_matching(), bsnprintf(), strfusec(), timeloop_init_current(), tm_dump(), tm_free() (+13 more)

### Community 24 - "babel/packets.c"
Cohesion: 0.08
Nodes (45): bmemcpy(), babel_auth_add_tlvs(), babel_auth_set_tx_overhead(), babel_auth_write_challenge(), babel_err_hook(), babel_read_ack_req(), babel_read_challenge_req(), babel_read_hello() (+37 more)

### Community 25 - "ospf_receive_lsupd"
Cohesion: 0.09
Nodes (44): tm_active(), ospf_dump_lsack(), ospf_lsack_body(), ospf_receive_lsack(), ospf_send_lsack_(), lsa_comp(), lsa_flooding_allowed(), lsa_ntoh_hdr() (+36 more)

### Community 26 - "unix/io.c"
Cohesion: 0.08
Nodes (45): sk_set_freebind(), call_rx_hook(), sk_alloc_bufs(), sk_connect(), sk_dump(), sk_dump_all(), sk_dump_ao_all(), sk_free() (+37 more)

### Community 27 - "tm_stop"
Cohesion: 0.09
Nodes (47): timers_count(), tm_stop(), rt_modify_stale(), rt_refresh_begin(), rt_refresh_end(), rt_schedule_prune(), bgp_active(), bgp_bfd_notify() (+39 more)

### Community 28 - "bsd-netlink/netlink.c"
Cohesion: 0.08
Nodes (43): kif_do_scan(), kif_sys_start(), krt_do_scan(), krt_sys_reconfigure(), krt_sys_shutdown(), krt_sys_start(), krt_table_id(), nl_async_err_hook() (+35 more)

### Community 29 - "linux/netlink.c"
Cohesion: 0.10
Nodes (44): nl_open_nexthop(), kif_sys_start(), krt_do_scan(), krt_replace_rte(), krt_sys_reconfigure(), krt_sys_shutdown(), krt_sys_start(), krt_table_id() (+36 more)

### Community 30 - "resource"
Cohesion: 0.05
Nodes (40): ca_free(), ev_dump(), idm_alloc(), idm_free(), u32_cto(), lp_dump(), lp_free(), lp_lookup() (+32 more)

### Community 31 - "bgp_proto"
Cohesion: 0.04
Nodes (49): bgp_proto, afi_map, ao, as4_session, bfd_req, cf, channel_count, channel_map (+41 more)

### Community 32 - "radv.c"
Cohesion: 0.08
Nodes (37): ip6_hton(), sk_tx_buffer_empty(), radv_err_hook(), radv_prepare_custom(), radv_prepare_dnssl(), radv_prepare_prefix(), radv_prepare_ra(), radv_prepare_rdnss() (+29 more)

### Community 33 - "trie_test.c"
Cohesion: 0.11
Nodes (38): benchmark_trie_dataset(), find_covering_nets(), get_exp_random(), get_inner_net(), get_outer_net(), get_random_ip4_subnet(), get_random_ip6_subnet(), get_random_prefix() (+30 more)

### Community 34 - "mac_test.c"
Cohesion: 0.08
Nodes (22): blake_in_fmt(), t_sha256_concating(), t_sha512_concating(), f1(), f3(), ror(), sha256_final(), sha256_init() (+14 more)

### Community 35 - "current_time"
Cohesion: 0.06
Nodes (39): config_timer_status(), u32_popcount(), MATCH_FUNC_NAME(), patmatch(), current_time(), timeloop_current(), tm_remains(), tm_set() (+31 more)

### Community 36 - "config"
Cohesion: 0.04
Nodes (41): config, channel_default_debug, cli_debug, current_scope, def_tables, err_chno, err_file_name, err_lino (+33 more)

### Community 37 - "channel"
Cohesion: 0.04
Nodes (45): channel, bmp_hack, channel, channel_state, debug, disabled, export_map, export_state (+37 more)

### Community 38 - "ospf/iface.c"
Cohesion: 0.12
Nodes (40): babel_iface_locked(), babel_iface_update_buffers(), add_nbma_node(), find_nbma_node_(), hello_timer_hook(), ifa_bufsize(), ifa_flood_queue_size(), ifa_tx_hdrlen() (+32 more)

### Community 39 - "bgp.h"
Cohesion: 0.05
Nodes (41): adata, bgp_cc_is_ipv4(), bgp_cc_is_ipv6(), bgp_export_state, attrs_seen, channel, err_reject, local_next_hop (+33 more)

### Community 40 - "rt-table.c"
Cohesion: 0.09
Nodes (39): lp_flush(), hc_alloc_table(), hc_delete_hostentry(), hc_hash(), hc_insert(), hc_new_hostentry(), hc_remove(), hc_resize() (+31 more)

### Community 41 - "init_list"
Cohesion: 0.07
Nodes (38): cfg_copy_list(), config_alloc(), config_parse(), init_event_check_points(), t_ev_run_list(), init_list(), resource_init(), timer_init() (+30 more)

### Community 42 - "rte"
Cohesion: 0.13
Nodes (36): channel_notify_limit(), rt_unlock_source(), rta_is_cached(), rte_cow(), rte_is_filtered(), rte_is_reachable(), rte_is_valid(), aspa_check() (+28 more)

### Community 43 - "mrt.c"
Cohesion: 0.09
Nodes (32): bstrsub(), mrt_bgp_buffer(), mrt_bgp_header(), mrt_buffer_flush(), mrt_buffer_grow(), mrt_buffer_init(), mrt_buffer_need(), mrt_buffer_pos() (+24 more)

### Community 44 - "bmp.c"
Cohesion: 0.09
Nodes (36): bmp_add_peer(), bmp_add_stream(), bmp_add_table(), bmp_close_socket(), bmp_connection_retry(), bmp_down(), bmp_feed_end(), bmp_find_peer() (+28 more)

### Community 45 - "ospf.c"
Cohesion: 0.08
Nodes (29): channel_graceful_restart_lock(), ospf_iface_shutdown(), add_area_nets(), fake_lsa_from_prefix_lsa(), lsa_compare_for_state(), oa_is_stub(), ospf_area_add(), ospf_area_reconfigure() (+21 more)

### Community 46 - "birdtest.c"
Cohesion: 0.06
Nodes (14): hmac_in_fmt(), bt_dump_backtrace(), bt_fmt_str(), bt_is_char(), bt_log_overall_result(), bt_log_result(), bt_log_suite_result(), bt_run_test_fn() (+6 more)

### Community 47 - "rtable"
Cohesion: 0.09
Nodes (36): trie_walk_init(), channel_roa_is_subscribed(), channel_roa_subscribe(), rtable, net_find(), net_find_valid(), net_get(), rt_is_flow() (+28 more)

### Community 48 - "add_tail"
Cohesion: 0.12
Nodes (31): add_head(), add_tail(), add_tail_list(), check_list(), insert_node(), list_length(), rem_node(), update_node() (+23 more)

### Community 49 - "rip.c"
Cohesion: 0.11
Nodes (35): iface_patt_find(), rip_add_rte(), rip_announce_rte(), rip_bfd_notify(), rip_find_iface(), rip_get_neighbor(), rip_if_notify(), rip_iface_link_up() (+27 more)

### Community 50 - "bgp.c"
Cohesion: 0.11
Nodes (32): proto_get_hostname(), bgp_close(), bgp_decision(), bgp_default_base_table(), bgp_default_igp_table(), bgp_disable_ao_key(), bgp_disable_ao_keys(), bgp_down() (+24 more)

### Community 51 - "rt-fib.c"
Cohesion: 0.10
Nodes (28): fib_user_to_node(), dump(), fib_check(), fib_delete(), fib_find(), fib_free(), fib_get(), fib_hash() (+20 more)

### Community 52 - "ospf/neighbor.c"
Cohesion: 0.11
Nodes (30): ipa_to_u32(), ospf_hello3_options(), ospf_receive_hello(), ospf_send_hello(), ackd_timer_hook(), can_do_adj(), changes_in_lsrtl(), elect_bdr() (+22 more)

### Community 53 - "slist_test.c"
Cohesion: 0.13
Nodes (27): dump(), fill_list(), fill_list2(), init_list__(), insert_node_(), is_empty_list_well_unlinked(), is_filled_list_well_linked(), show_list() (+19 more)

### Community 54 - "rip/packets.c"
Cohesion: 0.17
Nodes (31): ip4_class_mask(), ip4_masklen(), rip_check_authentication(), rip_err_hook(), rip_fill_authentication(), rip_fill_header(), rip_fill_update_hdr(), rip_get_auth_block() (+23 more)

### Community 55 - "proto_configure_channel"
Cohesion: 0.10
Nodes (35): channel_cmd_debug(), channel_config_get(), channel_config_new(), proto_add_channel(), proto_cf_find_channel(), proto_configure_channel(), proto_new(), proto_cf_main_channel() (+27 more)

### Community 56 - "proto"
Cohesion: 0.06
Nodes (32): proto, active, active_channels, cf, cf_new, channels, debug, disabled (+24 more)

### Community 57 - "mb_free"
Cohesion: 0.09
Nodes (27): hmap_free(), lmap_free(), mb_free(), action, bgp_free_bucket(), bgp_free_bucket_table(), bmp_peer_map_flush(), bmp_peer_map_free() (+19 more)

### Community 58 - "krt.c"
Cohesion: 0.14
Nodes (27): bmap_free(), kif_request_scan(), kif_shutdown(), krt_dump(), krt_export_net(), krt_flush_routes(), krt_got_route(), krt_got_route_async() (+19 more)

### Community 59 - "rta"
Cohesion: 0.13
Nodes (28): flow4_get_length(), flow4_set_length(), flow6_get_length(), flow6_set_length(), flow_hdr_length(), flow_read_length(), flow_read_pxlen(), t_read_length() (+20 more)

### Community 60 - "nest/iface.c"
Cohesion: 0.11
Nodes (31): ip_scope_text(), if_change_flags(), if_copy(), if_delete(), if_dump(), if_dump_all(), if_end_update(), if_feed_baby() (+23 more)

### Community 61 - "bgp_parse_state"
Cohesion: 0.06
Nodes (33): bgp_parse_state, add_path, as4_session, attr_len, attrs, attrs_seen, cached_rta, channel (+25 more)

### Community 62 - "rte_update2"
Cohesion: 0.11
Nodes (30): sl_alloc(), mpls_announce_fec(), mpls_get_key_rta(), nexthop_link(), nexthop_size(), rt_lock_hostentry(), rt_lock_source(), rta_cow() (+22 more)

### Community 63 - "bgp_channel"
Cohesion: 0.06
Nodes (28): bgp_ao_state, best_key, keys, bgp_channel, add_path_rx, add_path_tx, afi, base_table (+20 more)

### Community 64 - "bt_init"
Cohesion: 0.12
Nodes (31): main(), main(), main(), main(), main(), fill_expected_array(), init_buffer(), is_buffer_as_expected() (+23 more)

### Community 65 - "ev_schedule"
Cohesion: 0.09
Nodes (30): config_del_obstacle(), ev_active(), ev_enqueue(), ev_postpone(), ev_schedule(), ev_schedule_work(), channel_do_down(), channel_reload_loop() (+22 more)

### Community 66 - "l3vpn.c"
Cohesion: 0.08
Nodes (22): tree_node_count(), tree_walk(), rd_equal(), channel, channel_class, channel_config, config, mpls_show_ranges_cmd (+14 more)

### Community 67 - "hash.h"
Cohesion: 0.10
Nodes (22): mem_hash(), mem_hash_init(), mem_hash_mix(), mem_hash_mix_num(), mem_hash_mix_str(), mem_hash_value(), ptr_hash(), ea_hash() (+14 more)

### Community 68 - "krt-sock.c"
Cohesion: 0.09
Nodes (18): kif_sys_shutdown(), krt_buffer_release(), krt_buffer_update(), krt_capable(), krt_do_scan(), krt_get_max_tables(), krt_replace_rte(), krt_send_route() (+10 more)

### Community 69 - "a-set.c"
Cohesion: 0.19
Nodes (27): eclist_filter(), ec_set_cmp(), ec_set_contains(), ec_set_del(), ec_set_del_nontrans(), ec_set_max(), ec_set_min(), ec_set_sort() (+19 more)

### Community 70 - "bgp_conn"
Cohesion: 0.06
Nodes (29): bgp_conn, as4_session, bgp, channels_to_send, connect_timer, ext_messages, hold_time, hold_timer (+21 more)

### Community 71 - "log.c"
Cohesion: 0.10
Nodes (21): val_format_str(), t_bstrcmp(), t_fmt_order(), t_simple(), bstrcmp(), lp_strdup(), bmp_reconfigure(), debug_safe() (+13 more)

### Community 72 - "bgp_channel_config"
Cohesion: 0.07
Nodes (30): bgp_channel_config, add_path, afi, aigp, aigp_originate, base_table, c, cost (+22 more)

### Community 73 - "nest/neighbor.c"
Cohesion: 0.17
Nodes (27): if_in_vrf(), if_connected(), if_connected_any(), if_intersect(), ifa_better(), ifa_intersect(), neigh_down(), neigh_dump() (+19 more)

### Community 74 - "bfd/io.c"
Cohesion: 0.12
Nodes (26): bfd_free_iface(), bfd_notify_kick(), bfd_reconfigure(), birdloop_current(), birdloop_init_current(), birdloop_mask_wakeups(), birdloop_new(), birdloop_stop() (+18 more)

### Community 75 - "bmp_proto"
Cohesion: 0.07
Nodes (24): bmp_proto, bmp_node, cf, connect_retry_timer, local_addr, monitoring_rib, msgbuf, p (+16 more)

### Community 76 - "die"
Cohesion: 0.12
Nodes (24): ev_run(), ev_run_list(), ev_run_list_limited(), timers_fire(), timers_first(), xrealloc(), birdloop_main(), events_fire() (+16 more)

### Community 77 - "nl_send_route"
Cohesion: 0.12
Nodes (25): krt_capable(), krt_replace_rte(), nh_bufsize(), nl_add_attr(), nl_add_attr_ip4(), nl_add_attr_ip6(), nl_add_attr_ipa(), nl_add_attr_mpls() (+17 more)

### Community 78 - "bitmap.c"
Cohesion: 0.18
Nodes (24): b1024_and(), b1024_first_zero(), b1024_first_zero_in_range(), b1024_last_one(), b1024_last_one_in_range(), b1024_or(), b256_and(), b256_first_zero() (+16 more)

### Community 79 - "ip_test.c"
Cohesion: 0.10
Nodes (22): ip4_pton(), ip6_equal(), ip6_pton(), ip6_shift_left(), ip6_shift_right(), main(), t_ip4_prefix_equal(), t_ip6_prefix_equal() (+14 more)

### Community 80 - "ospf_rx_hook"
Cohesion: 0.15
Nodes (21): ipa_nonzero2(), mac_type_length(), memset32(), max_mac_length(), password_find(), password_find_by_id(), password_find_by_value(), password_verify() (+13 more)

### Community 81 - "lp_alloc_adata"
Cohesion: 0.13
Nodes (27): get_ip4(), ipa_zero2(), get_u32s(), as_path_contains_as4(), as_path_contains_confed(), as_path_strip_confed(), as_path_to_old(), int_set_sort() (+19 more)

### Community 82 - "BIRDPrinter"
Cohesion: 0.10
Nodes (7): BIRDFExecStackPrinter, BIRDFInstPrinter, BIRDFLineItemPrinter, BIRDFLinePrinter, BIRDFValPrinter, BIRDFValStackPrinter, BIRDPrinter

### Community 83 - "mac.c"
Cohesion: 0.24
Nodes (19): hash_buffer(), hash_final(), hash_init(), hash_update(), hmac_final(), hmac_init(), hmac_update(), mac_cleanup() (+11 more)

### Community 84 - "proto-hooks.c"
Cohesion: 0.11
Nodes (10): get_attr(), get_route_info(), get_status(), neigh_notify(), preexport(), rt_notify(), rte_better(), rte_insert() (+2 more)

### Community 85 - "rfree"
Cohesion: 0.18
Nodes (24): rfree(), babel_open_socket(), sk_start(), bfd_open_rx_sk(), bfd_open_rx_sk_bound(), bfd_open_tx_sk(), bgp_free_prefix_table(), bgp_open() (+16 more)

### Community 86 - "a-path.c"
Cohesion: 0.16
Nodes (20): as_path_16to32(), as_path_32to16(), as_path_compare(), as_path_contains(), as_path_cut(), as_path_get_first(), as_path_get_first_regular(), as_path_get_last() (+12 more)

### Community 87 - "proto_config"
Cohesion: 0.09
Nodes (21): channel_limit, limit, state, proto_config, channels, class, debug, disabled (+13 more)

### Community 88 - "u32"
Cohesion: 0.09
Nodes (21): bgp_ao_key, active, failed, key, n, bgp_bucket, eattrs, hash (+13 more)

### Community 89 - "bmp_route_monitor_notify"
Cohesion: 0.19
Nodes (20): bmp_connected(), bmp_default_buffer(), bmp_fix_common_hdr(), bmp_init_msg_serialize(), bmp_is_peer_global_instance(), bmp_peer_down_notif_msg_serialize(), bmp_peer_up_notif_msg_serialize(), bmp_put_bgp_hdr() (+12 more)

### Community 90 - "birdcl.c"
Cohesion: 0.11
Nodes (7): cleanup(), input_read(), lastnb(), more_end(), sig_handler(), drop_uid(), set_capabilities()

### Community 91 - "sym_scope"
Cohesion: 0.09
Nodes (19): cf_find_symbol_cfg(), keyword, name, value, sym_scope, active, block, name (+11 more)

### Community 92 - "ipa_equal"
Cohesion: 0.25
Nodes (22): nl_parse_addr4(), nl_parse_addr6(), ip4_or(), ip6_masklen(), ipa_classify(), ipa_classify_net(), ipa_equal(), ipa_equal_wildcard() (+14 more)

### Community 93 - "blake2s.c"
Cohesion: 0.19
Nodes (17): load32(), store16(), store32(), blake2s_compress(), blake2s_final(), blake2s_increment_counter(), blake2s_init(), blake2s_init0() (+9 more)

### Community 94 - "perf.c"
Cohesion: 0.12
Nodes (12): xstrdup(), xmalloc(), rte, rte_update(), rte_update3(), perf_feed_begin(), perf_feed_end(), perf_loop() (+4 more)

### Community 95 - "static.c"
Cohesion: 0.17
Nodes (19): proto_shutdown_mpls_map(), l3vpn_shutdown(), static_add_rte(), static_bfd_notify(), static_decide(), static_dump(), static_dump_rte(), static_get_source() (+11 more)

### Community 96 - "channel_config"
Cohesion: 0.10
Nodes (20): channel_config, bmp_hack, channel, copy, debug, in_filter, in_keep_filtered, in_limit (+12 more)

### Community 97 - "attrs.h"
Cohesion: 0.20
Nodes (15): lclist_filter(), ec_set_add(), aggregator_contains_as4(), ec_as2(), ec_as4(), ec_get(), ec_hi(), ec_ip4() (+7 more)

### Community 98 - "tree_test.c"
Cohesion: 0.27
Nodes (18): build_tree(), build_tree_rec(), f_new_tree(), get_balanced_full_subtree(), get_balanced_full_tree(), get_balanced_tree_with_ranged_values(), get_degenerated_left_tree(), get_max_value_in_unbalanced_tree() (+10 more)

### Community 99 - "vpn_rd"
Cohesion: 0.17
Nodes (15): hash_value(), u32_hash0(), u64_cmp(), u64_hash(), u64_hash0(), rd_hash0(), rd_nonzero(), rd_to_u64() (+7 more)

### Community 100 - "blake2b_state"
Cohesion: 0.11
Nodes (16): blake2b_state, buf, buflen, f, h, last_node, outlen, t (+8 more)

### Community 101 - "cli.c"
Cohesion: 0.18
Nodes (14): cli_alloc_out(), cli_cmd_read_hook(), cli_copy_message(), cli_echo(), cli_event(), cli_free(), cli_free_out(), cli_hello() (+6 more)

### Community 102 - "proto_stats"
Cohesion: 0.10
Nodes (20): proto_stats, exp_routes, exp_updates_accepted, exp_updates_filtered, exp_updates_received, exp_updates_rejected, exp_withdraws_accepted, exp_withdraws_received (+12 more)

### Community 103 - "protocol_class"
Cohesion: 0.10
Nodes (20): protocol_class, PROTOCOL_AGGREGATOR, PROTOCOL_BABEL, PROTOCOL_BFD, PROTOCOL_BGP, PROTOCOL_BMP, PROTOCOL_DEVICE, PROTOCOL_DIRECT (+12 more)

### Community 104 - "ea_get_int"
Cohesion: 0.11
Nodes (11): ea_get_int(), babel_get_attr(), babel_get_route_info(), babel_rte_better(), babel_rte_igp_metric(), ospf_rte_better(), rip_get_attr(), rip_get_route_info() (+3 more)

### Community 105 - "cmds.c"
Cohesion: 0.17
Nodes (13): f_eval(), f_eval_buf(), run_function(), rmemsize(), slab, get_memsize(), t_slab(), test_alloc() (+5 more)

### Community 106 - "blake2b.c"
Cohesion: 0.22
Nodes (15): secure_zero_memory(), blake2b_compress(), blake2b_final(), blake2b_increment_counter(), blake2b_init(), blake2b_init0(), blake2b_init_key(), blake2b_init_param() (+7 more)

### Community 107 - "uint_cmp"
Cohesion: 0.22
Nodes (17): compare_prefixes(), uint_cmp(), flow_uint_cmp(), ip4_compare(), ip6_compare(), rd_compare(), net_compare(), net_compare_flow4() (+9 more)

### Community 108 - "nl_parse_route"
Cohesion: 0.22
Nodes (17): ip4_ntoh(), nl_async_msg(), nl_checkin(), nl_parse_addr(), nl_parse_attrs(), nl_parse_link(), nl_parse_metrics(), nl_parse_multipath() (+9 more)

### Community 109 - "rte"
Cohesion: 0.22
Nodes (14): as_path_getlen(), rta_as_path_is_empty(), bgp_get_neighbor(), bgp_get_route_info(), bgp_rte_better(), bgp_rte_igp_metric(), bgp_rte_mergable(), bgp_rte_recalculate() (+6 more)

### Community 110 - "bgp_caps"
Cohesion: 0.11
Nodes (17): bgp_caps, af_count, af_data, any_add_path, any_ext_next_hop, as4_number, as4_support, enhanced_refresh (+9 more)

### Community 111 - "tcp_ao_getsockopt_ext"
Cohesion: 0.11
Nodes (18): tcp_ao_getsockopt_ext, addr, alg_name, get_all, ifindex, is_current, is_rnext, key (+10 more)

### Community 112 - "val_compare"
Cohesion: 0.17
Nodes (16): adata_empty(), clist_filter(), clist_match_set(), clist_set_type(), eclist_match_set(), eclist_set_type(), lclist_match_set(), lclist_set_type() (+8 more)

### Community 113 - "if"
Cohesion: 0.14
Nodes (17): commit-messages, image, rules, script, stage, rules, docker-debian-11-i386, after_script (+9 more)

### Community 114 - "checksum.c"
Cohesion: 0.22
Nodes (8): add32(), ipsum_calc(), ipsum_calc_block(), ipsum_calculate(), ipsum_verify(), ipsum_calculate_expected(), t_calculate(), t_verify()

### Community 115 - "hash_test.c"
Cohesion: 0.24
Nodes (14): fill_hash(), init_hash_(), print_rate_of_fulfilment(), t_insert2_find(), t_insert_find(), t_insert_find_random(), t_walk(), t_walk_delsafe_delete() (+6 more)

### Community 116 - "printf.c"
Cohesion: 0.24
Nodes (11): buffer_vprint(), bvsnprintf(), bvsprintf(), fmt_order(), lp_sprintf(), lp_vsprintf(), mb_sprintf(), mb_vsprintf() (+3 more)

### Community 117 - "a-set_test.c"
Cohesion: 0.21
Nodes (15): ec_format(), ec_set_format(), int_set_format(), lc_format(), generate_set_sequence(), t_set_ec_contains(), t_set_ec_delete(), t_set_ec_format() (+7 more)

### Community 118 - "proto_build"
Cohesion: 0.12
Nodes (17): proto_build(), dev_build(), babel_build(), bfd_build(), bgp_build(), bmp_build(), l3vpn_build(), mrt_build() (+9 more)

### Community 119 - "benchmark_fib_dataset"
Cohesion: 0.21
Nodes (11): benchmark_fib_dataset(), net_match(), t_bench_fib_datasets(), t_fib_walk(), t_match_random_net(), bt_random_net_subset(), bt_random_nets(), bt_read_net_file() (+3 more)

### Community 120 - "bgp_af_caps"
Cohesion: 0.12
Nodes (16): bgp_af_caps, add_path, afi, ext_next_hop, gr_able, gr_af_flags, llgr_able, llgr_flags (+8 more)

### Community 122 - "bmap_test"
Cohesion: 0.29
Nodes (13): bmap_clear(), bmap_max(), bmap_set(), bmap_test(), hmap_check(), hmap_clear(), hmap_first_zero(), hmap_max() (+5 more)

### Community 123 - "lists_test.c"
Cohesion: 0.24
Nodes (13): fill_list(), fill_list2(), init_list__(), insert_node_(), is_empty_list_well_unlinked(), is_filled_list_well_linked(), show_list(), t_add_head() (+5 more)

### Community 124 - "tcp_ao_del_ext"
Cohesion: 0.12
Nodes (14): tcp_ao_del_ext, addr, current_key, del_async, ifindex, keyflags, prefix, rcvid (+6 more)

### Community 125 - "tcp_ao_info_opt_ext"
Cohesion: 0.12
Nodes (15): tcp_ao_info_opt_ext, accept_icmps, ao_required, current_key, pkt_ao_required, pkt_bad, pkt_dropped_icmp, pkt_good (+7 more)

### Community 126 - "tcp_ao_add_ext"
Cohesion: 0.12
Nodes (15): tcp_ao_add_ext, addr, alg_name, ifindex, key, keyflags, keylen, maclen (+7 more)

### Community 127 - "unaligned.h"
Cohesion: 0.19
Nodes (10): get_u24(), get_u64(), put_u24(), put_u32s(), put_u64(), put_u8(), bgp_aigp_get_metric(), bgp_aigp_get_tlv() (+2 more)

### Community 128 - ".gitlab-ci.yml"
Cohesion: 0.14
Nodes (13): .if-stable, if, when, .if-tag, if, when, .never-tag, if (+5 more)

### Community 129 - "IMG_NAME"
Cohesion: 0.14
Nodes (14): docker-centos-7-amd64, after_script, script, stage, tags, variables, docker-opensuse-15.2-amd64, after_script (+6 more)

### Community 130 - "lp_alloc"
Cohesion: 0.21
Nodes (11): lp_alloc(), lp_allocu(), int_set_add(), int_set_cmp(), int_set_contains(), int_set_max(), int_set_min(), int_set_prepend() (+3 more)

### Community 131 - "protocol"
Cohesion: 0.14
Nodes (12): channel_class, channel_size, config_size, protocol, channel_mask, config_size, n, name (+4 more)

### Community 132 - "bfd/packets.c"
Cohesion: 0.30
Nodes (11): bfd_err_hook(), bfd_fill_authentication(), bfd_format_flags(), bfd_pack_flags(), bfd_pack_vdiag(), bfd_pkt_get_diag(), bfd_pkt_get_state(), bfd_pkt_get_version() (+3 more)

### Community 133 - "changes"
Cohesion: 0.15
Nodes (13): .docker, after_script, docker-debian-12-amd64, after_script, rules, script, stage, tags (+5 more)

### Community 134 - "blake2b_param"
Cohesion: 0.15
Nodes (13): blake2b_param, depth, digest_length, fanout, inner_length, key_length, leaf_length, node_depth (+5 more)

### Community 135 - "blake2s_param"
Cohesion: 0.15
Nodes (12): blake2s_param, depth, digest_length, fanout, inner_length, key_length, leaf_length, node_depth (+4 more)

### Community 136 - "ospf3_get_prefix"
Cohesion: 0.22
Nodes (9): lsa_get_options(), ospf3_4to6(), ospf3_6to4(), ospf3_get_addr(), ospf3_get_prefix(), ospf3_put_addr(), ospf3_put_prefix(), show_lsa_prefix() (+1 more)

### Community 138 - "buffer"
Cohesion: 0.50
Nodes (12): buffer, pm_format(), rte_block_format(), rte_format(), val_dump(), val_format(), tree_format(), tree_node_format() (+4 more)

### Community 139 - "mpls_fec_map"
Cohesion: 0.17
Nodes (11): mpls_fec_map, channel, domain, handle, mpls_rts, mpls_scope, pool, slabs (+3 more)

### Community 140 - "bitops_test.c"
Cohesion: 0.27
Nodes (8): check_log2(), check_mask(), t_log2(), t_masklen(), t_mkmask(), u32_masklen_expected(), u32_log2(), bt_naive_pow()

### Community 141 - "blake2.h"
Cohesion: 0.18
Nodes (10): blake2b_context, buf, state, type, blake2s_context, buf, state, type (+2 more)

### Community 142 - "mpls_domain"
Cohesion: 0.17
Nodes (11): mpls_domain, cf, handles, label_count, labels, n, name, pool (+3 more)

### Community 143 - "bmp_config"
Cohesion: 0.17
Nodes (10): bmp_config, c, local_addr, monitoring_rib_in_post_policy, monitoring_rib_in_pre_policy, station_ip, station_port, sys_descr (+2 more)

### Community 144 - "rt_show_net"
Cohesion: 0.24
Nodes (8): f_eval_rte(), f_run(), f_run_args(), interpret(), tbf_limit(), rt_show_net(), mrt_rib_table_dump(), log_rl()

### Community 145 - "blake2-impl.h"
Cohesion: 0.27
Nodes (7): load16(), load48(), load64(), rotr32(), rotr64(), store48(), store64()

### Community 146 - "current_real_time"
Cohesion: 0.29
Nodes (9): current_real_time(), babel_auth_check(), babel_auth_check_mac(), babel_auth_sign(), babel_mac_build_phdr(), babel_process_packet(), babel_read_subtlvs(), babel_read_tlv() (+1 more)

### Community 147 - "uint"
Cohesion: 0.18
Nodes (10): mpls_channel, c, mpls_channel_config, c, domain, label_policy, range, domain (+2 more)

### Community 149 - "bitops.h"
Cohesion: 0.24
Nodes (5): u32_clz(), u32_ctz(), u32_hash(), u64_popcount(), uint_is_pow2()

### Community 150 - "heap_test.c"
Cohesion: 0.58
Nodes (8): init_heap(), is_heap_valid(), show_heap(), t_heap_0(), t_heap_delete(), t_heap_increase_decrease(), t_heap_insert(), t_heap_insert_random()

### Community 151 - "md5.c"
Cohesion: 0.36
Nodes (4): byteReverse(), md5_final(), md5_transform(), md5_update()

### Community 152 - "mpls_fec"
Cohesion: 0.20
Nodes (9): mpls_fec, handle, hash, label, next_k, next_l, policy, state (+1 more)

### Community 153 - "babel_handle_seqno_request"
Cohesion: 0.31
Nodes (9): babel_find_entry(), babel_find_seqno_request_target(), babel_get_entry(), babel_handle_route_request(), babel_handle_seqno_request(), babel_rt_notify(), babel_send_retraction(), babel_trigger_iface_update() (+1 more)

### Community 154 - "include_file_stack"
Cohesion: 0.22
Nodes (9): include_file_stack, chno, depth, fd, file_name, lino, prev, toklen (+1 more)

### Community 156 - "mpls_range_config"
Cohesion: 0.22
Nodes (8): mpls_range_config, domain, implicit, length, n, name, range, start

### Community 157 - "mpls_range"
Cohesion: 0.22
Nodes (9): mpls_range, cf, hi, label_count, lo, n, name, removed (+1 more)

### Community 158 - "current_time_now"
Cohesion: 0.31
Nodes (7): cmd_dump_file(), current_time_now(), dump_to_file_flush(), dump_to_file_init(), dump_to_file_run(), dump_to_file_write(), async_dump()

### Community 159 - "variables"
Cohesion: 0.25
Nodes (8): variables, DEBIAN_FRONTEND, DOCKER_CMD, GIT_STRATEGY, IMG_BASE, LC_ALL, STAYRTR_BINARY, TOOLS_DIR

### Community 160 - "setkey.h"
Cohesion: 0.36
Nodes (3): setkey_md5(), setkey_open_socket(), setkey_send()

### Community 161 - "sha1.c"
Cohesion: 0.43
Nodes (3): sha1_final(), sha1_transform(), sha1_update()

### Community 162 - "sl_free"
Cohesion: 0.32
Nodes (8): sl_free(), babel_announce_retraction(), babel_expire_requests(), babel_expire_route(), babel_expire_routes_(), babel_expire_sources(), babel_flush_route(), babel_remove_seqno_request()

### Community 163 - "mpls_domain_config"
Cohesion: 0.25
Nodes (7): mpls_domain_config, domain, dynamic_range, n, name, ranges, static_range

### Community 164 - "bmp_stream"
Cohesion: 0.25
Nodes (7): bmp_stream, bgp, n, next, sender, sync, table

### Community 165 - "log_open_udp"
Cohesion: 0.25
Nodes (6): resolve_hostname(), rf_fdopen(), rf_file(), rf_open(), sock_new(), log_open_udp()

### Community 166 - "tag-collect"
Cohesion: 0.29
Nodes (7): paths, tag-collect, artifacts, image, rules, script, stage

### Community 167 - "docker-centos-8-amd64"
Cohesion: 0.29
Nodes (7): docker-centos-8-amd64, after_script, rules, script, stage, tags, variables

### Community 168 - "docker-debian-10-amd64"
Cohesion: 0.29
Nodes (7): docker-debian-10-amd64, after_script, rules, script, stage, tags, variables

### Community 169 - "docker-debian-10-i386"
Cohesion: 0.29
Nodes (7): docker-debian-10-i386, after_script, rules, script, stage, tags, variables

### Community 170 - "docker-debian-11-amd64"
Cohesion: 0.29
Nodes (7): docker-debian-11-amd64, after_script, rules, script, stage, tags, variables

### Community 171 - "docker-docbuilder"
Cohesion: 0.29
Nodes (7): docker-docbuilder, after_script, rules, script, stage, tags, variables

### Community 172 - "docker-fedora-32-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-32-amd64, after_script, rules, script, stage, tags, variables

### Community 173 - "docker-fedora-33-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-33-amd64, after_script, rules, script, stage, tags, variables

### Community 174 - "docker-fedora-34-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-34-amd64, after_script, rules, script, stage, tags, variables

### Community 175 - "docker-fedora-35-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-35-amd64, after_script, rules, script, stage, tags, variables

### Community 176 - "docker-fedora-36-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-36-amd64, after_script, rules, script, stage, tags, variables

### Community 177 - "docker-fedora-37-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-37-amd64, after_script, rules, script, stage, tags, variables

### Community 178 - "docker-fedora-38-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-38-amd64, after_script, rules, script, stage, tags, variables

### Community 179 - "docker-fedora-39-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-39-amd64, after_script, rules, script, stage, tags, variables

### Community 180 - "docker-fedora-40-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-40-amd64, after_script, rules, script, stage, tags, variables

### Community 181 - "docker-fedora-41-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-41-amd64, after_script, rules, script, stage, tags, variables

### Community 182 - "docker-fedora-42-amd64"
Cohesion: 0.29
Nodes (7): docker-fedora-42-amd64, after_script, rules, script, stage, tags, variables

### Community 183 - "docker-opensuse-15.0-amd64"
Cohesion: 0.29
Nodes (7): docker-opensuse-15.0-amd64, after_script, rules, script, stage, tags, variables

### Community 184 - "docker-opensuse-15.1-amd64"
Cohesion: 0.29
Nodes (7): docker-opensuse-15.1-amd64, after_script, rules, script, stage, tags, variables

### Community 185 - "docker-opensuse-15.3-amd64"
Cohesion: 0.29
Nodes (7): docker-opensuse-15.3-amd64, after_script, rules, script, stage, tags, variables

### Community 186 - "docker-opensuse-15.4-amd64"
Cohesion: 0.29
Nodes (7): docker-opensuse-15.4-amd64, after_script, rules, script, stage, tags, variables

### Community 187 - "docker-opensuse-15.5-amd64"
Cohesion: 0.29
Nodes (7): docker-opensuse-15.5-amd64, after_script, rules, script, stage, tags, variables

### Community 188 - "docker-ubuntu-18.04-amd64"
Cohesion: 0.29
Nodes (7): docker-ubuntu-18.04-amd64, after_script, rules, script, stage, tags, variables

### Community 189 - "main"
Cohesion: 0.38
Nodes (4): download_file(), is_loopback_http_url(), main(), install-codebase-memory.sh script

### Community 190 - "lp_state"
Cohesion: 0.29
Nodes (5): lp_state, current, large, ptr, total_large

### Community 191 - "strtoul.c"
Cohesion: 0.38
Nodes (4): bstrhextobin(), bstrtoul10(), bstrtoul16(), fromxdigit()

### Community 192 - "as_path_prepend"
Cohesion: 0.29
Nodes (6): as_path_filter(), count_asn_in_array(), t_as_path_converting(), t_path_format(), t_path_include(), as_path_prepend()

### Community 193 - "ea_set_attr"
Cohesion: 0.43
Nodes (4): ea_set_attr(), ea_set_attr_data(), ea_set_attr_ptr(), ea_set_attr_u32()

### Community 194 - "tcp-ao.h"
Cohesion: 0.29
Nodes (5): tcp_ao_repair_ext, rcv_isn, rcv_sne, snd_sne, snt_isn

### Community 195 - "kif_force_scan"
Cohesion: 0.43
Nodes (6): kif_force_scan(), kif_reconfigure(), kif_scan(), krt_init_scan(), krt_scan(), krt_scan_all()

### Community 196 - "blake2b_constant"
Cohesion: 0.33
Nodes (6): blake2b_constant, BLAKE2B_BLOCKBYTES, BLAKE2B_KEYBYTES, BLAKE2B_OUTBYTES, BLAKE2B_PERSONALBYTES, BLAKE2B_SALTBYTES

### Community 197 - "blake2s_constant"
Cohesion: 0.33
Nodes (6): blake2s_constant, BLAKE2S_BLOCKBYTES, BLAKE2S_KEYBYTES, BLAKE2S_OUTBYTES, BLAKE2S_PERSONALBYTES, BLAKE2S_SALTBYTES

### Community 198 - "bmp_table"
Cohesion: 0.33
Nodes (5): bmp_table, channel, next, table, uc

### Community 199 - "krt_scan_timer_kick"
Cohesion: 0.33
Nodes (5): krt_feed_end(), krt_if_notify(), krt_reload_routes(), krt_scan_all_timer_kick(), krt_scan_timer_kick()

### Community 200 - "test-bird.sh"
Cohesion: 0.80
Nodes (4): cleanup(), failed(), test-bird.sh script, stop_bird()

### Community 201 - "mpls_handle"
Cohesion: 0.40
Nodes (4): mpls_handle, label_count, n, range

### Community 202 - "bmp_peer"
Cohesion: 0.40
Nodes (4): bmp_peer, bgp, next, streams

### Community 204 - "monitoring_rib"
Cohesion: 0.50
Nodes (4): monitoring_rib, in_post_policy, in_pre_policy, local

### Community 205 - "random_bytes"
Cohesion: 0.50
Nodes (3): random_bytes(), random_init(), read_urandom_fd()

### Community 206 - "resclass"
Cohesion: 0.67
Nodes (3): resclass, name, size

### Community 207 - "resmem"
Cohesion: 0.67
Nodes (3): resmem, effective, overhead

### Community 208 - "proto_spec"
Cohesion: 0.67
Nodes (3): proto_spec, patt, ptr

## Knowledge Gaps
- **784 isolated node(s):** `buf`, `buflen`, `f`, `h`, `last_node` (+779 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1403 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ip_addr` connect `ip_addr` to `ospf_is_v2`, `topology.c`, `bgp/packets.c`, `ip.h`, `proto.c`, `bgp_config`, `ospf3_get_prefix`, `rpki.c`, `babel.c`, `sock`, `bmp_config`, `net_addr`, `bfd.c`, `current_real_time`, `babel/packets.c`, `ospf_receive_lsupd`, `unix/io.c`, `bsd-netlink/netlink.c`, `linux/netlink.c`, `bgp_proto`, `radv.c`, `log_open_udp`, `ospf/iface.c`, `rt-table.c`, `mrt.c`, `rip.c`, `rt-fib.c`, `ospf/neighbor.c`, `rip/packets.c`, `mb_free`, `rte_update2`, `bgp_channel`, `bgp_channel_config`, `nest/neighbor.c`, `bmp_proto`, `nl_send_route`, `ospf_rx_hook`, `lp_alloc_adata`, `rfree`, `bmp_route_monitor_notify`, `ipa_equal`, `nl_parse_route`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 105 inferred relationships involving `current_time()` (e.g. with `config_alloc()` and `nl_open_sock()`) actually correct?**
  _`current_time()` has 105 INFERRED edges - model-reasoned connections that need verification._
- **What connects `buf`, `buflen`, `f` to the rest of the system?**
  _784 weakly-connected nodes found - possible missing edges._
- **Should `net.h` be split into smaller, more focused modules?**
  _Cohesion score 0.04098544232922732 - nodes in this community are weakly interconnected._
- **Why does `sock` connect `sock` to `bgp/packets.c`, `bfd/packets.c`, `rpki.c`, `main.c`, `bfd.c`, `current_real_time`, `ip_addr`, `babel/packets.c`, `unix/io.c`, `tm_stop`, `bsd-netlink/netlink.c`, `linux/netlink.c`, `bgp_proto`, `radv.c`, `log_open_udp`, `ospf/iface.c`, `bmp.c`, `bgp.c`, `rip/packets.c`, `mb_free`, `krt-sock.c`, `bfd/io.c`, `bmp_proto`, `die`, `ospf_rx_hook`, `rfree`, `u32`, `cli.c`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 82 inferred relationships involving `add_tail()` (e.g. with `cfg_copy_list()` and `make_random_prefix_list()`) actually correct?**
  _`add_tail()` has 82 INFERRED edges - model-reasoned connections that need verification._
- **Should `ospf_is_v2` be split into smaller, more focused modules?**
  _Cohesion score 0.06655974338412189 - nodes in this community are weakly interconnected._