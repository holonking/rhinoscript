# this is a tutorial note of eto controls

#<ComboBox>
combo=ComboBox()
combo.Width=140
for item in listStr:
    combo.Items.Add(item)
combo.SelectedIndex=0
item=combo.Items[combo.SelectedIndex].Text
