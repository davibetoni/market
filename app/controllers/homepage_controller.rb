class HomepageController < ApplicationController
  def index
  end

  def get_info
    param1 = 'valor1'
    param2 = 'valor2'

    system("python3 app/jobs/esi/esi.py #{param1} #{param2}")

    sleep(2)
  end
end
