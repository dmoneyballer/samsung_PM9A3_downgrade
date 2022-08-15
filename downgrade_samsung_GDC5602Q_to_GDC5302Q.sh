#!/bin/bash -e


function do_one_drive() {
	(
		nvme_dev=/dev/nvme/nvme$1
		for fw in '/tmp/samsung_PM9A3_downgrade/General_PM9A3_GDC5502Q_Noformat.bin' '/tmp/samsung_PM9A3_downgrade/Bridge_PM9A3_GHC5502B.bin' '/tmp/samsung_PM9A3_downgrade/General_PM9A3_GDC5402Q_Noformat.bin' '/tmp/samsung_PM9A3_downgrade/Bridge_PM9A3_GHC5402B.bin' '/tmp/samsung_PM9A3_downgrade/General_PM9A3_GDC5302Q_Noformat.bin'; do
			echo "Starting downgrade to $fw on $nvme_dev"
			echo "resetting  $nvme_dev"
			/ybd/firmware/nvme reset $nvme_dev
			echo "fw-download $nvme_dev"
			echo "/ybd/firmware/nvme fw-download $nvme_dev --fw='$fw'"
			/ybd/firmware/nvme fw-download $nvme_dev --fw=$fw
			echo "fw-activate $nvme_dev"
			/ybd/firmware/nvme fw-activate $nvme_dev --slot=0 --action=3
			sleep 4
			echo "resetting  $nvme_dev"
			/ybd/firmware/nvme reset $nvme_dev
		done
	) | tee /tmp/nvme_$1_downgrade.log
}


for ((n=0;n<8;n++)); do
	do_one_drive $n &
done
wait
